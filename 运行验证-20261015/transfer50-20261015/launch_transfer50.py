#!/usr/bin/env python3
"""Run the authorized fixed offline evaluation once, with an owned process deadline."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    tmp.replace(path)


def bounded_run(command, cwd, receipt_path, log_path, max_seconds,
                progress_path=None, interval=30):
    receipt_path, log_path = Path(receipt_path), Path(log_path)
    if max_seconds <= 0:
        raise ValueError('Positive deadline required')
    record = {'started_at_utc': now(), 'parent_pid': os.getpid(),
              'command': list(command), 'max_wall_seconds': max_seconds,
              'status': 'STARTING', 'scope': 'one owned child process group only'}
    with receipt_path.open('x') as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    process = None
    started = time.monotonic()
    interrupted = {'signal': None}

    def stop_owned():
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def remember_signal(number, frame):
        interrupted['signal'] = number
        stop_owned()

    old_handlers = {}
    try:
        for number in (signal.SIGINT, signal.SIGTERM):
            old_handlers[number] = signal.signal(number, remember_signal)
        with log_path.open('xb') as log:
            if interrupted['signal'] is not None:
                record.update(status='INTERRUPTED', finished_at_utc=now(),
                              child_exit_code=None, received_signal=interrupted['signal'],
                              wall_seconds=time.monotonic()-started)
                save(receipt_path, record)
                return record
            process = subprocess.Popen(command, cwd=str(cwd), stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            if interrupted['signal'] is not None:
                stop_owned()
            record.update(child_pid=process.pid, status='RUNNING')
            save(receipt_path, record)
            print(json.dumps({'status': 'RUNNING', 'child_pid': process.pid,
                              'max_wall_seconds': max_seconds}), flush=True)
            while process.poll() is None:
                if interrupted['signal'] is not None:
                    stop_owned()
                    process.wait()
                    break
                remaining = max_seconds - (time.monotonic() - started)
                if remaining <= 0:
                    stop_owned()
                    process.wait()
                    record['status'] = 'DEADLINE_STOP'
                    break
                try:
                    process.wait(timeout=min(interval, remaining))
                except subprocess.TimeoutExpired:
                    progress = None
                    if progress_path is not None and Path(progress_path).is_file():
                        try:
                            progress = json.loads(Path(progress_path).read_text())
                        except (ValueError, OSError):
                            pass
                    print(json.dumps({'status': 'PROCESS_LIVE', 'child_pid': process.pid,
                                      'wall_seconds': round(time.monotonic()-started, 1),
                                      'progress': progress}, ensure_ascii=False), flush=True)
            if interrupted['signal'] is not None:
                record['status'] = 'INTERRUPTED'
            elif record['status'] != 'DEADLINE_STOP':
                record['status'] = 'CHILD_EXITED'
            record.update(finished_at_utc=now(), child_exit_code=process.returncode,
                          wall_seconds=time.monotonic()-started,
                          received_signal=interrupted['signal'])
            save(receipt_path, record)
            print(json.dumps(record, ensure_ascii=False), flush=True)
            return record
    except BaseException as exc:
        if process is not None and process.poll() is None:
            stop_owned()
            process.wait()
        record.update(status='LAUNCHER_ERROR', finished_at_utc=now(),
                      error=f'{type(exc).__name__}: {exc}')
        save(receipt_path, record)
        raise
    finally:
        for number, handler in old_handlers.items():
            signal.signal(number, handler)


def main():
    here = Path(__file__).resolve().parent
    parent = here.parent
    protocol_path = here / 'protocol.json'
    protocol = json.loads(protocol_path.read_text())
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != protocol['launcher_sha256']:
        raise SystemExit('STOP launcher differs from frozen protocol')
    adapter = here / 'evaluate_transfer50.py'
    actual_hash = hashlib.sha256(adapter.read_bytes()).hexdigest()
    if actual_hash != protocol['adapter_sha256']:
        raise SystemExit('STOP adapter differs from frozen protocol')
    if protocol['max_wall_seconds'] != 14400 or protocol['max_inference_seconds'] != 14400:
        raise SystemExit('STOP resource limit differs from authorized proposal')
    if protocol['device'] != 'cpu' or protocol['threads'] != 6:
        raise SystemExit('STOP CPU configuration differs from authorized proposal')
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[key] = '6'
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      HF_DATASETS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                      PYTHONUNBUFFERED='1')
    command = [str(parent / '.venv/bin/python'), str(adapter),
               '--protocol', str(protocol_path), '--data', str(parent / 'data/hourly.parquet'),
               '--source-root', str(parent / 'vendor/Kronos'),
               '--model-dir', str(parent / 'weights/small'),
               '--tokenizer-dir', str(parent / 'weights/tokenizer'),
               '--out', str(here / 'results')]
    result = bounded_run(command, here, here / 'launch-attempt.json',
                         here / 'execution.log', 14400,
                         progress_path=here / 'results/progress.json')
    raise SystemExit(0 if result.get('status') == 'CHILD_EXITED'
                     and result.get('child_exit_code') == 0 else 2)


if __name__ == '__main__':
    main()
