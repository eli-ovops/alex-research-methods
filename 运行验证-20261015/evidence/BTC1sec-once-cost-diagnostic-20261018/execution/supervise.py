"""Bounded supervisor, only monitors this supervisor and its single worker PID."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def utc():
    return dt.datetime.now(dt.timezone.utc)


def save(name, obj):
    p = HERE / name
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    os.replace(tmp, p)


def identity(path):
    p = Path(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return {'sha256': h.hexdigest(), 'bytes': p.stat().st_size}


def rss(pids):
    # macOS ps RSS is KiB; exact known PIDs only, no all-user process scan.
    p = subprocess.run(['/bin/ps', '-o', 'rss=', '-p', ','.join(map(str, pids))],
                       capture_output=True, text=True, check=False)
    return sum(int(v) * 1024 for v in p.stdout.split())


def disk_bytes():
    return sum(p.stat().st_size for p in HERE.parent.rglob('*') if p.is_file())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'run'])
    parser.add_argument('--approval')
    args = parser.parse_args()
    config = json.loads((HERE / 'config.json').read_text())
    auth = json.loads(Path(config['authorization']).read_text())
    # Verify authority identity before spawn, without any market processing.
    if identity(config['authorization']) != config['frozen_inputs'][config['authorization']]:
        raise ValueError('Authorization identity changed')
    previous = sorted(HERE.glob('session-*-receipt.json'))
    used = sum(json.loads(p.read_text())['elapsed_seconds'] for p in previous)
    number = len(previous) + 1
    prefix = 'session-%03d-%s' % (number, args.stage)
    if args.stage == 'run':
        if (HERE / 'formal-started.lock').exists() or (HERE / 'run-invocation.lock').exists():
            raise ValueError('Single-use run lock exists, no second invocation')
        with (HERE / 'run-invocation.lock').open('x') as f:
            json.dump({'utc': utc().isoformat(), 'approval': args.approval, 'supervisor_pid': os.getpid()}, f)
    start = time.monotonic()
    command = [sys.executable, '-I', '-B', '-S', str(HERE / 'diagnostic.py'), args.stage]
    if args.approval:
        command += ['--approval', str(Path(args.approval).resolve())]
    env = dict(os.environ)
    for k in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS']:
        env[k] = '2'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['TMPDIR'] = str(HERE / 'tmp')
    (HERE / 'tmp').mkdir(exist_ok=True)
    deadline = dt.datetime.fromisoformat(auth['hard_deadline_utc'])
    if utc() >= deadline or used >= auth['caps']['compute_seconds']:
        raise ValueError('Deadline/compute budget expired')
    with (HERE / (prefix + '.stdout.txt')).open('x') as out, (HERE / (prefix + '.stderr.txt')).open('x') as err:
        process = subprocess.Popen(command, stdout=out, stderr=err, env=env, cwd=HERE,
                                   start_new_session=True)
        peak = 0
        disk_peak = 0
        reason = None
        started = utc().isoformat()
        print(json.dumps({'session': prefix, 'supervisor_pid': os.getpid(), 'worker_pid': process.pid,
                          'started_utc': started}), flush=True)
        while True:
            elapsed = time.monotonic() - start
            memory = rss([os.getpid(), process.pid])
            peak = max(peak, memory)
            disk_peak = max(disk_peak, disk_bytes())
            live = {'stage': args.stage, 'session': prefix, 'started_utc': started, 'observed_utc': utc().isoformat(),
                    'worker_pid': process.pid, 'supervisor_pid': os.getpid(), 'elapsed_seconds': elapsed,
                    'cumulative_seconds_including_prior': used + elapsed, 'RSS_peak_combined_bytes': peak,
                    'new_directory_disk_peak_bytes': disk_peak}
            save(prefix + '.live.json', live)
            if memory > auth['caps']['RSS_bytes']:
                reason = 'RSS_LIMIT'
            elif disk_peak > auth['caps']['new_disk_bytes']:
                reason = 'DISK_LIMIT'
            elif used + elapsed > auth['caps']['compute_seconds']:
                reason = 'COMPUTE_LIMIT'
            elif utc() >= deadline:
                reason = 'UTC_DEADLINE'
            if reason:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                break
            if process.poll() is not None:
                break
            time.sleep(0.25)
        code = process.wait()
    elapsed = time.monotonic() - start
    receipt = dict(live, ended_utc=utc().isoformat(), exit_code=code, stop_reason=reason,
                   elapsed_seconds=elapsed, cumulative_seconds_including_prior=used + elapsed,
                   command=command, known_processes_only=True, no_background_worker=True,
                   resource_sampling_seconds=0.25, threads='stdlib single worker, env caps2',
                   actual_model_effort='UNKNOWN')
    save('session-%03d-receipt.json' % number, receipt)
    print(json.dumps({'session': prefix, 'exit_code': code, 'stop_reason': reason,
                      'cumulative_seconds': used + elapsed}), flush=True)
    raise SystemExit(code if not reason else 2)


if __name__ == '__main__':
    main()
