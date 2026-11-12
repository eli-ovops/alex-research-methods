"""One public blob acquisition and bounded passive gzip JSON format/time QC."""
import base64
import collections
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def now():
    return dt.datetime.now(dt.timezone.utc)


def save(name, obj):
    p = HERE / name
    temp = p.with_suffix(p.suffix + '.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    os.replace(temp, p)


def ident(path):
    p = Path(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return {'bytes': p.stat().st_size, 'sha256': h.hexdigest()}


def utc_ns(n):
    seconds, ns = divmod(n, 1000000000)
    return dt.datetime.fromtimestamp(seconds, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S') + '.%09dZ' % ns


def integer(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.lstrip('-').isdigit():
        return int(v)
    return None


def worker(scope):
    with (HERE / 'single-acquisition.lock').open('x') as f:
        json.dump({'utc': now().isoformat(), 'pid': os.getpid(), 'attempt': 1}, f)
    target = scope['target']
    command = ['gh', 'api', '--method', 'GET', '--include', '-H',
               'Accept: application/vnd.github.raw+json', target['api_url']]
    start = now().isoformat()
    gh = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    save('child-status.json', {'pid': gh.pid, 'active': True})
    total = 0
    wire = HERE / 'sample-blob.original-wire.bin'
    with wire.open('xb') as f:
        while True:
            b = gh.stdout.read(65536)
            if not b:
                break
            total += len(b)
            if total > scope['caps']['wire_max_bytes']:
                gh.terminate()
                gh.wait()
                raise ValueError('Wire cap exceeded; no retry')
            f.write(b)
    stderr = gh.stderr.read(65536)
    code = gh.wait()
    save('child-status.json', {'pid': gh.pid, 'active': False})
    (HERE / 'acquisition.stderr.txt').write_bytes(stderr)
    raw = wire.read_bytes()
    sep = raw.find(b'\r\n\r\n')
    width = 4
    if sep < 0:
        sep, width = raw.find(b'\n\n'), 2
    if sep < 0 or sep > 65536:
        raise ValueError('Missing HTTP headers')
    header = raw[:sep].decode('ascii', 'replace')
    status = int(header.splitlines()[0].split()[1])
    body = raw[sep + width:]
    acquisition = {'started_utc': start, 'ended_utc': now().isoformat(), 'source': target['api_url'],
                   'method': 'GET', 'attempts': 1, 'gh_exit_code': code, 'HTTP_status': status,
                   'original_wire': ident(wire), 'body_bytes': len(body), 'command': command}
    save('acquisition-receipt.json', acquisition)
    if code != 0 or status != 200:
        raise ValueError('Public GET failed; no retry or alternate resource')
    encoding = 'raw gzip media response'
    if body.lstrip().startswith(b'{'):
        obj = json.loads(body)
        if obj.get('sha') != target['blob'] or obj.get('encoding') != 'base64':
            raise ValueError('Unexpected JSON blob identity/encoding')
        body = base64.b64decode(obj['content'], validate=False)
        encoding = 'passive base64 decode of same response, no second request'
    if len(body) != target['expected_bytes']:
        raise ValueError('Actual blob byte count differs from fixed metadata')
    actual = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    if actual != target['blob']:
        raise ValueError('Git blob mismatch')
    path = HERE / 'btcusdt_20240808.gz'
    with path.open('xb') as f:
        f.write(body)
    acquisition.update(encoding=encoding, gzip_identity=ident(path), Git_blob_actual=actual,
                       Git_blob_matches=True)
    save('acquisition-receipt.json', acquisition)
    del raw, body
    counts = collections.Counter()
    prefix_widths, streams, events, symbols = [collections.Counter() for _ in range(4)]
    clock_fields = {}
    field_prev = {}
    previous = None
    first = last = None
    markers = collections.Counter()
    marker_examples = []
    first_records = []
    decoded = 0
    with gzip.open(path, 'rb') as f:
        while True:
            line = f.readline(scope['caps']['max_line_bytes'] + 1)
            if not line:
                break
            decoded += len(line)
            if len(line) > scope['caps']['max_line_bytes'] or decoded > scope['caps']['decoded_stream_bytes']:
                raise ValueError('Decoded line/stream cap exceeded')
            counts['raw_lines'] += 1
            if not line.strip():
                counts['empty_lines'] += 1
                continue
            parts = line.strip().split(None, 1)
            if len(parts) != 2 or not parts[0].isdigit():
                counts['invalid_integer_prefix_or_missing_JSON'] += 1
                continue
            prefix = int(parts[0])
            prefix_widths[str(len(parts[0]))] += 1
            counts['integer_prefix_lines'] += 1
            if previous is not None:
                counts['prefix_adjacent_comparisons'] += 1
                counts['prefix_equal'] += int(prefix == previous)
                counts['prefix_backwards'] += int(prefix < previous)
            previous = prefix
            first = prefix if first is None else first
            last = prefix
            try:
                obj = json.loads(parts[1])
            except (ValueError, UnicodeDecodeError):
                counts['JSON_parse_failures'] += 1
                continue
            if not isinstance(obj, dict):
                counts['JSON_not_object'] += 1
                continue
            counts['JSON_objects'] += 1
            stream = str(obj.get('stream', '<missing>'))
            data = obj.get('data', obj)
            if not isinstance(data, dict):
                counts['data_not_object'] += 1
                continue
            event = str(data.get('e', '<missing>'))
            symbol = str(data.get('s', '<missing>'))
            streams[stream] += 1
            events[event] += 1
            symbols[symbol] += 1
            if len(first_records) < 5:
                first_records.append({'line': counts['raw_lines'], 'prefix': prefix, 'stream': stream,
                                      'event': event, 'symbol': symbol, 'data_keys': sorted(data.keys())})
            for field in ['E', 'T']:
                key = stream + '::' + field
                stats = clock_fields.setdefault(key, {'present': 0, 'absent': 0, 'integer': 0,
                    'noninteger': 0, 'raw_integer_widths': {}, 'equal': 0, 'backwards': 0, 'comparisons': 0})
                if field not in data:
                    stats['absent'] += 1
                    continue
                stats['present'] += 1
                v = integer(data[field])
                if v is None:
                    stats['noninteger'] += 1
                    continue
                stats['integer'] += 1
                w = str(len(str(abs(v))))
                stats['raw_integer_widths'][w] = stats['raw_integer_widths'].get(w, 0) + 1
                if key in field_prev:
                    stats['comparisons'] += 1
                    stats['equal'] += int(v == field_prev[key])
                    stats['backwards'] += int(v < field_prev[key])
                field_prev[key] = v
            found = []
            label = (stream + ' ' + event).lower()
            if 'snapshot' in label:
                found.append('snapshot_named_stream_or_event')
            if 'lastUpdateId' in data or 'lastUpdateId' in obj:
                found.append('lastUpdateId_key')
            if 'reset' in label:
                found.append('reset_named_stream_or_event')
            if 'clear' in label:
                found.append('clear_named_stream_or_event')
            markers.update(found)
            if found and len(marker_examples) < 10:
                marker_examples.append({'line': counts['raw_lines'], 'prefix': prefix,
                                        'stream': stream, 'event': event, 'markers': found})
            if counts['raw_lines'] % 10000 == 0:
                save('progress.json', {'stage': 'gzip_JSON_scan', 'rows': counts['raw_lines'],
                                      'decoded_bytes': decoded, 'utc': now().isoformat(), 'pid': os.getpid()})
    # Reading gzip EOF validates all gzip member CRCs and declared lengths; no unpickle or replay.
    for name in ['empty_lines', 'invalid_integer_prefix_or_missing_JSON', 'JSON_parse_failures',
                 'JSON_not_object', 'data_not_object', 'prefix_equal', 'prefix_backwards']:
        counts.setdefault(name, 0)
    qc = {'status': 'COMPLETE_PASSIVE_QC_NOT_CAUSAL_REPLAY_OR_PROFIT', 'finished_utc': now().isoformat(),
          'gzip_EOF_CRC_verified': True, 'gzip_identity': acquisition['gzip_identity'],
          'Git_blob_matches': True, 'decoded_stream_bytes': decoded, 'counts': dict(counts),
          'prefix_widths': dict(prefix_widths), 'first_prefix_raw': first, 'last_prefix_raw': last,
          'first_UTC_assuming_documented_ns': utc_ns(first) if first is not None else None,
          'last_UTC_assuming_documented_ns': utc_ns(last) if last is not None else None,
          'span_seconds_assuming_documented_ns': (last - first) / 1e9 if first is not None else None,
          'prefix_time_unit_basis': 'Official same-name current DataPreparation tutorial says raw firsttoken ns local receipt; not clock-sync verification',
          'stream_counts': dict(streams), 'event_counts': dict(events), 'symbol_counts': dict(symbols),
          'E_T_raw_field_stats_per_stream': clock_fields,
          'E_T_units_and_latency': 'No new field-unit primary proof read in this unit; only integer format/order, no E/T UTC or latency subtraction',
          'marker_counts': dict(markers), 'marker_examples_max10': marker_examples,
          'first_records_metadata_only': first_records,
          'limits': ['Marker presence alone not complete initial book or gap-free sequence proof.',
                     'No L2 rebuild, sorting/repair, collector version or clock synchronization certification.',
                     'No price movement, future label, return, cost-space or model calculation.'],
          'acquisitions': 1, 'QC_scans': 1, 'models_or_trades': 0, 'actual_model_effort': 'UNKNOWN'}
    save('QC.json', qc)


def main():
    config = json.loads((HERE / 'config.json').read_text())
    scope = json.loads(Path(config['scope']).read_text())
    for path, ref in config['inputs'].items():
        if ident(path) != ref:
            raise ValueError('Frozen source/notice/scope identity mismatch')
    if '--worker' in sys.argv:
        start = time.monotonic()
        try:
            worker(scope)
            save('worker-terminal.json', {'status': 'COMPLETE', 'utc': now().isoformat(), 'pid': os.getpid(),
                 'seconds': time.monotonic() - start, 'ru_maxrss_bytes_macos': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        except Exception as e:
            save('worker-terminal.json', {'status': 'STOP_NO_RETRY', 'utc': now().isoformat(),
                 'error_type': type(e).__name__, 'message': str(e), 'seconds': time.monotonic() - start})
            raise SystemExit(1)
        return
    with (HERE / 'supervisor-started.lock').open('x') as f:
        json.dump({'utc': now().isoformat(), 'pid': os.getpid()}, f)
    start = time.monotonic()
    env = dict(os.environ, OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2',
               PYTHONDONTWRITEBYTECODE='1')
    command = [sys.executable, '-I', '-B', '-S', str(Path(__file__).resolve()), '--worker']
    peak = disk_peak = 0
    reason = None
    with (HERE / 'worker.stdout.txt').open('x') as out, (HERE / 'worker.stderr.txt').open('x') as err:
        proc = subprocess.Popen(command, stdout=out, stderr=err, env=env, start_new_session=True, cwd=HERE)
        print(json.dumps({'supervisor_pid': os.getpid(), 'worker_pid': proc.pid, 'start_utc': now().isoformat()}), flush=True)
        while True:
            pids = [os.getpid(), proc.pid]
            child = HERE / 'child-status.json'
            if child.exists():
                info = json.loads(child.read_text())
                if info.get('active'):
                    pids.append(info['pid'])
            ps = subprocess.run(['/bin/ps', '-o', 'rss=', '-p', ','.join(map(str, pids))],
                                capture_output=True, text=True)
            mem = sum(int(x) * 1024 for x in ps.stdout.split())
            peak = max(peak, mem)
            disk_peak = max(disk_peak, sum(p.stat().st_size for p in HERE.parent.rglob('*') if p.is_file()))
            elapsed = time.monotonic() - start
            if mem > scope['caps']['RSS_bytes']:
                reason = 'RSS_LIMIT'
            elif disk_peak > scope['caps']['new_disk_bytes']:
                reason = 'DISK_LIMIT'
            elif elapsed > scope['caps']['compute_seconds']:
                reason = 'COMPUTE_LIMIT'
            elif now() >= dt.datetime.fromisoformat(scope['hard_deadline_utc']):
                reason = 'UTC_LIMIT'
            save('resource-live.json', {'utc': now().isoformat(), 'worker_pid': proc.pid, 'supervisor_pid': os.getpid(),
                 'known_PIDs_including_active_GH': pids, 'elapsed_seconds': elapsed, 'RSS_peak_combined_bytes': peak,
                 'disk_peak_bytes': disk_peak})
            if reason and proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                break
            if proc.poll() is not None:
                break
            time.sleep(0.1)
        code = proc.wait()
    receipt = {'exit_code': code, 'stop_reason': reason, 'ended_utc': now().isoformat(),
               'elapsed_seconds': time.monotonic() - start, 'RSS_peak_combined_bytes_sampled': peak,
               'new_directory_disk_peak_bytes': disk_peak, 'sampling_seconds': 0.1,
               'known_task_PIDs_only': True, 'no_active_worker': True, 'command': command}
    save('execution-terminal.json', receipt)
    print(json.dumps(receipt), flush=True)
    raise SystemExit(code if not reason else 2)


if __name__ == '__main__':
    main()
