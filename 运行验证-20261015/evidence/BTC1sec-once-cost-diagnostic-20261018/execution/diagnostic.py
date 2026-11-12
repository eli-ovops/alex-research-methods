"""Owned standard-library, single-use, ideal quote cost-space diagnostic. No model."""
import argparse
import array
import collections
import csv
import datetime as dt
from decimal import Decimal, localcontext, getcontext
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import resource
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
getcontext().prec = 80  # Also preserve high-precision timestamp subtraction outside quote context.
ZERO = Decimal(0)
TWO = Decimal(2)
BP = Decimal(10000)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(name, obj):
    path = HERE / name
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    os.replace(temp, path)


def identity(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return {'sha256': h.hexdigest(), 'bytes': path.stat().st_size}


def verify(refs):
    for path, expected in refs.items():
        if identity(path) != expected:
            raise ValueError('Input identity mismatch: ' + str(path))


def quantile_summary(values):
    if not len(values):
        return {'n': 0, 'mean': None, 'p50': None, 'p95': None, 'p99': None, 'max': None,
                'positive': 0, 'positive_fraction': None, 'zero': 0}
    ordered = sorted(values)  # One metric/slice at a time, exact Type7.
    out = {'n': len(values), 'mean': math.fsum(values) / len(values), 'max': ordered[-1],
           'positive': sum(v > 0 for v in values), 'zero': sum(v == 0 for v in values)}
    out['positive_fraction'] = out['positive'] / len(values)
    for p, key in [(0.5, 'p50'), (0.95, 'p95'), (0.99, 'p99')]:
        h = (len(ordered) - 1) * p
        lo = math.floor(h)
        hi = math.ceil(h)
        out[key] = ordered[lo] + (ordered[hi] - ordered[lo]) * (h - lo)
    del ordered
    return out


def spaces(m0, s0, m1, s1, fees):
    """Decimal text inputs; mathematical envelope, not orders or wealth returns."""
    a0, b0 = m0 + s0 / TWO, m0 - s0 / TWO
    a1, b1 = m1 + s1 / TWO, m1 - s1 / TWO
    gl, gs = b1 - a0, b0 - a1
    gross = max(ZERO, gl, gs) * BP / m0
    cap = max(ZERO, gl / (a0 + b1), gs / (b0 + a1)) * BP
    out = {'gross_bp': gross, 'per_leg_fee_capacity_bp': cap}
    for f in fees:
        rate = Decimal(f) / BP
        out['remaining_bp_fee_' + str(f)] = max(ZERO, gl - rate * (a0 + b1),
                                                  gs - rate * (b0 + a1)) * BP / m0
    return out


def pair_reasons(previous, current):
    reasons = []
    if not previous['valid']:
        reasons.append('previous_invalid_numeric_or_quote')
    if not current['valid']:
        reasons.append('current_invalid_numeric_or_quote')
    exact = (current['exact_time'] - previous['exact_time'] if 'exact_time' in current else
             Decimal(str((current['time'] - previous['time']).total_seconds())))
    if exact != Decimal(1):
        reasons.append('not_exact_one_second')
    return reasons


def synthetic():
    with localcontext() as ctx:
        ctx.prec = 80
        fees = [0, 1, 5, 10, 25]
        a = spaces(Decimal('100'), Decimal('2'), Decimal('104'), Decimal('2'), fees)
        assert a['gross_bp'] == Decimal('200')
        assert a['per_leg_fee_capacity_bp'] == Decimal(2) / Decimal(204) * BP
        assert a['remaining_bp_fee_25'] == Decimal('149')
        assert a['remaining_bp_fee_0'] == a['gross_bp']
        assert all(a['remaining_bp_fee_' + str(x)] >= a['remaining_bp_fee_' + str(y)]
                   for x, y in zip(fees, fees[1:]))
        b = spaces(Decimal('104'), Decimal('2'), Decimal('100'), Decimal('2'), fees)
        assert b['gross_bp'] == Decimal(2) * BP / Decimal(104)
        c = spaces(Decimal('100'), Decimal('2'), Decimal('100'), Decimal('2'), fees)
        assert all(v == 0 for v in c.values())
        q = quantile_summary(array.array('d', [0, 1, 2, 3]))
        assert q['p50'] == 1.5 and abs(q['p95'] - 2.85) < 1e-12
        t = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        p = {'time': t, 'valid': True}
        assert pair_reasons(p, {'time': t + dt.timedelta(seconds=1), 'valid': True}) == []
        assert pair_reasons(p, {'time': t + dt.timedelta(seconds=2), 'valid': True}) == ['not_exact_one_second']
        assert len(pair_reasons(p, {'time': t + dt.timedelta(seconds=2), 'valid': False})) == 2
        assert pair_reasons({'time': t, 'exact_time': Decimal('1.000000001'), 'valid': True},
                            {'time': t + dt.timedelta(seconds=1), 'exact_time': Decimal('2.000000002'),
                             'valid': True}) == ['not_exact_one_second']
        assert quantile_summary(array.array('d'))['mean'] is None
    return {'status': 'PASS_SYNTHETIC_ONLY', 'tests': ['long_short_decimal_formula', 'per_leg_fee',
            'zero_space', 'exact_type7', 'adjacent_exclusions', 'empty_undefined'],
            'market_records_read': 0, 'diagnostic_runs': 0}


def preflight(config):
    verify(config['frozen_inputs'])
    auth = json.loads(Path(config['authorization']).read_text())
    if not auth['user_authorized'] or dt.datetime.now(dt.timezone.utc) >= dt.datetime.fromisoformat(auth['hard_deadline_utc']):
        raise ValueError('Authorization/deadline unavailable')
    assert config['fees_per_leg_bp'] == [0, 1, 5, 10, 25]
    assert config['download_mode'] == 'complete_GET_200'
    assert len(config['header']) == 156 and config['header'][0] == ''
    result = synthetic()
    result.update(utc=utc(), python=sys.version, pid=os.getpid(), sources={
        str(HERE / n): identity(HERE / n) for n in ['diagnostic.py', 'supervise.py', 'config.json']},
        frozen_inputs=config['frozen_inputs'], formal_claim_exists=(HERE / 'formal-started.lock').exists(),
        environment={n: os.environ.get(n) for n in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                    'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'PYTHONDONTWRITEBYTECODE']})
    if result['formal_claim_exists']:
        raise ValueError('Formal claim already exists')
    save('preflight.json', result)
    return result['status']


def archive_download(config):
    target = HERE / 'BTC_1sec.fixed-v1.zip'
    part = HERE / 'BTC_1sec.fixed-v1.zip.partial'
    req = urllib.request.Request(config['url'], headers={'If-Match': '"' + config['etag'] + '"'})
    # Default TLS, no cookies, credentials, SDK, Range fallback or retries.
    receipt = {'started_utc': utc(), 'original_url': config['url'], 'mode': config['download_mode'],
               'request_headers': {'If-Match': '"' + config['etag'] + '"'}, 'attempt': 1}
    h = hashlib.sha256()
    count = 0
    with urllib.request.urlopen(req, timeout=30) as response:
        final = urllib.parse.urlsplit(response.url)
        receipt.update(status=response.status, final_url_without_query=urllib.parse.urlunsplit(
            (final.scheme, final.netloc, final.path, '', '')),
            headers={n: response.headers.get(n) for n in ['Content-Length', 'Content-Type', 'ETag',
                     'Last-Modified', 'x-goog-generation', 'x-goog-hash']})
        save('download-start.json', receipt)
        if response.status != 200 or int(response.headers.get('Content-Length', '-1')) != config['zip_bytes']:
            raise ValueError('Complete GET status/declared size mismatch')
        if response.headers.get('ETag', '').strip('"') != config['etag']:
            raise ValueError('Archive ETag identity mismatch')
        with part.open('xb') as out:
            next_progress = 16 * 1024 * 1024
            while True:
                chunk = response.read(min(1024 * 1024, config['zip_bytes'] + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                if count > config['zip_bytes']:
                    raise ValueError('Received-byte cap exceeded')
                h.update(chunk)
                out.write(chunk)
                if count >= next_progress:
                    save('progress.json', {'utc': utc(), 'pid': os.getpid(), 'stage': 'download', 'bytes': count})
                    next_progress += 16 * 1024 * 1024
    if count != config['zip_bytes']:
        raise ValueError('Received byte count incomplete')
    os.replace(part, target)
    receipt.update(ended_utc=utc(), bytes=count, sha256=h.hexdigest(), path=str(target))
    save('download-receipt.json', receipt)
    return target, {'sha256': h.hexdigest(), 'bytes': count}


def member_info(z, config):
    infos = z.infolist()
    if len(infos) != 1:
        raise ValueError('Expected exactly one ZIP member')
    i = infos[0]
    if (i.filename != 'BTC_1sec.csv' or i.file_size != config['member_bytes'] or
            i.CRC != int(config['member_crc32'], 16) or i.compress_type != 8 or i.flag_bits & 1):
        raise ValueError('Member identity/size/CRC declaration mismatch')
    return i


class CountedStream(io.RawIOBase):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.count = 0
        self.digest = hashlib.sha256()
        self.crc = 0

    def readable(self):
        return True

    def readinto(self, buffer):
        data = self.source.read(len(buffer))
        self.count += len(data)
        self.digest.update(data)
        self.crc = zlib.crc32(data, self.crc)
        buffer[:len(data)] = data
        return len(data)


def records(path, config):
    with zipfile.ZipFile(path) as z:
        i = member_info(z, config)
        with z.open(i) as binary:
            counted = CountedStream(binary)
            with io.TextIOWrapper(io.BufferedReader(counted, buffer_size=65536), encoding='utf-8-sig', newline='') as text:
                csv.field_size_limit(262144)
                reader = csv.reader(text, strict=True)
                if next(reader) != config['header']:
                    raise ValueError('CSV header mismatch')
                for n, row in enumerate(reader, 1):
                    if len(row) != 156:
                        raise ValueError('CSV row width mismatch at ' + str(n))
                    yield n, row
                # Iteration reaches actual EOF; ZipExtFile verifies full CRC.
                if counted.count != config['member_bytes'] or counted.crc != int(config['member_crc32'], 16):
                    raise ValueError('Actual decoded byte count/CRC mismatch')
                config['_last_stream_integrity'] = {'bytes': counted.count,
                    'sha256': counted.digest.hexdigest(), 'crc32': format(counted.crc, '08x')}


def row_state(row, indexes):
    ti, mi, si, static, numeric, flow = indexes
    stamp = dt.datetime.fromisoformat(row[ti])
    if stamp.utcoffset() != dt.timedelta(0):
        raise ValueError('Global clock must have explicit UTC offset')
    # datetime truncates fractional digits beyond microseconds. Preserve original decimal clock.
    match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.(\d+))?(?:Z|\+00:00)', row[ti])
    if not match or len(match.group(3) or '') > 30:
        raise ValueError('Unrecognized or excessive-precision UTC timestamp')
    base = dt.datetime.fromisoformat(match.group(1) + 'T' + match.group(2) + '+00:00')
    delta = base - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    with localcontext() as clock_context:
        clock_context.prec = 80
        exact_time = Decimal(delta.days * 86400 + delta.seconds) + Decimal('0.' + (match.group(3) or '0'))
    reasons = collections.Counter()
    values = {}
    for j in numeric:
        if not row[j].strip():
            reasons['empty_numeric'] += 1
            continue
        try:
            v = float(row[j])
        except ValueError:
            reasons['unparseable_numeric'] += 1
            continue
        if not math.isfinite(v):
            reasons['nonfinite_numeric'] += 1
        else:
            values[j] = v
    if values.get(mi, 0) <= 0:
        reasons['nonpositive_midpoint'] += 1
    if si in values and values[si] < 0:
        reasons['negative_spread'] += 1
    if mi in values and si in values and values[mi] - values[si] / 2 <= 0:
        reasons['nonpositive_model_bid'] += 1
    for j in static:
        if j in values and values[j] < 0:
            reasons['negative_static_depth'] += 1
    valid = not reasons
    return {'time': stamp, 'exact_time': exact_time, 'date': stamp.date().isoformat(), 'valid': valid,
            'reasons': reasons, 'values': values,
            'negative_flow_cells': sum(values.get(j, 0) < 0 for j in flow)}


def indexes_for(config):
    head = config['header']
    ti = head.index('system_time')
    return (ti, head.index('midpoint'), head.index('spread'),
            [i for i, n in enumerate(head) if re.fullmatch(r'(bids|asks)_notional_\d+', n)],
            [i for i in range(len(head)) if i != ti],
            [i for i, n in enumerate(head) if re.fullmatch(r'(bids|asks)_(market|limit|cancel)_notional_\d+', n)])


def pass1(path, config, zip_id):
    idx = indexes_for(config)
    head = config['header']
    daily = collections.defaultdict(collections.Counter)
    counts = collections.Counter()
    interval_counts = collections.Counter()
    seen_full, seen_state = set(), set()
    distance_abs, distance_relative = array.array('d'), array.array('d')
    prev = None
    prior_state_hash = None
    first, last = None, None
    examples = []
    ti, mi, si = idx[:3]
    ai, bi = head.index('asks_distance_0'), head.index('bids_distance_0')
    for n, row in records(path, config):
        current = row_state(row, idx)
        if prev and current['exact_time'] <= prev['exact_time']:
            raise ValueError('Global non-increasing time at row ' + str(n))
        date = current['date']
        daily[date]['rows'] += 1
        counts['rows'] += 1
        if first is None:
            first = row[ti]
        last = row[ti]
        counts.update(current['reasons'])
        daily[date].update(current['reasons'])
        counts['negative_flow_cells'] += current['negative_flow_cells']
        daily[date]['negative_flow_cells'] += current['negative_flow_cells']
        if not current['valid']:
            counts['invalid_rows'] += 1
            daily[date]['invalid_rows'] += 1
            if len(examples) < 10:
                examples.append({'row': n, 'time': row[ti], 'reasons': dict(current['reasons'])})
        full_hash = hashlib.blake2b(json.dumps(row, separators=(',', ':')).encode(), digest_size=16).digest()
        state_hash = hashlib.blake2b(json.dumps([v for j, v in enumerate(row) if j not in (0, ti)],
                                             separators=(',', ':')).encode(), digest_size=16).digest()
        if full_hash in seen_full:
            counts['duplicate_full_hash'] += 1
            daily[date]['duplicate_full_hash'] += 1
        if state_hash in seen_state:
            counts['duplicate_excluding_time_index_hash'] += 1
            daily[date]['duplicate_excluding_time_index_hash'] += 1
        if state_hash == prior_state_hash:
            counts['adjacent_unchanged_state'] += 1
            daily[date]['adjacent_unchanged_state'] += 1
        seen_full.add(full_hash)
        seen_state.add(state_hash)
        prior_state_hash = state_hash
        values = current['values']
        if all(j in values for j in [mi, si, ai, bi]):
            observed = values[si]
            predicted = values[mi] * (values[ai] - values[bi])
            err = abs(observed - predicted)
            if math.isfinite(err):
                distance_abs.append(err)
            else:
                counts['distance_error_nonfinite_descriptive_only'] += 1
            if observed != 0 and math.isfinite(err / abs(observed)):
                distance_relative.append(err / abs(observed))
        if prev:
            # Pair dates are always the starting row's UTC label date, including midnight crossing.
            pair_date = prev['date']
            counts['adjacent_pairs'] += 1
            daily[pair_date]['adjacent_pairs'] += 1
            difference = current['exact_time'] - prev['exact_time']
            interval_counts[str(difference)] += 1
            reasons = pair_reasons(prev, current)
            if reasons:
                counts['excluded_pairs'] += 1
                daily[pair_date]['excluded_pairs'] += 1
                for reason in reasons:
                    counts['pair_' + reason] += 1
                    daily[pair_date]['pair_' + reason] += 1
            else:
                counts['eligible_pairs'] += 1
                daily[pair_date]['eligible_pairs'] += 1
        prev = current
        if n % 25000 == 0:
            save('progress.json', {'stage': 'pass1_QC', 'rows': n, 'utc': utc(), 'pid': os.getpid()})
    result = {'status': 'PASS_FILE_QC_WITH_COUNTED_ROW_EXCLUSIONS', 'finished_utc': utc(),
              'archive_identity': zip_id, 'member_integrity': config['_last_stream_integrity'],
              'EOF_and_CRC': True, 'counts': dict(counts),
              'daily': {k: dict(v) for k, v in daily.items()}, 'first_time': first, 'last_time': last,
              'interval_seconds': dict(interval_counts), 'examples_max10': examples,
              'duplicate_definition': '128-bit BLAKE2b of parsed textual fields; probabilistic hash equality, not logical uniqueness guarantee',
              'distance_descriptive_only_no_gate': {'absolute_error': quantile_summary(distance_abs),
                  'relative_error_nonzero_spread': quantile_summary(distance_relative)},
              'unit_and_arrival_semantics': 'Not certified by magnitudes, algebra or UTC timestamp labels'}
    save('pass1-QC.json', result)
    save('pass1-seal.json', {'utc': utc(), 'archive': {str(path): zip_id},
                           'QC': {str(HERE / 'pass1-QC.json'): identity(HERE / 'pass1-QC.json')}})
    return result


def pass2(path, config, qc, zip_id):
    if identity(path) != zip_id:
        raise ValueError('Archive changed before pass2')
    idx = indexes_for(config)
    mi, si = idx[1:3]
    fees = config['fees_per_leg_bp']
    names = ['gross_bp', 'per_leg_fee_capacity_bp'] + ['remaining_bp_fee_' + str(f) for f in fees]
    values = {name: array.array('d') for name in names}
    ranges = {}
    counts = collections.Counter()
    positive_exact = collections.Counter()
    daily_positive_exact = collections.defaultdict(collections.Counter)
    daily_exclusions = collections.defaultdict(collections.Counter)
    prev = None
    with localcontext() as ctx:
        ctx.prec = 80
        for n, row in records(path, config):
            # Pass1 already checked all columns. The same deterministic row-validity policy is reused.
            current = row_state(row, idx)
            current['m_text'], current['s_text'] = row[mi], row[si]
            if prev:
                reasons = pair_reasons(prev, current)
                date = prev['date']
                counts['adjacent_pairs'] += 1
                if reasons:
                    counts['excluded_pairs'] += 1
                    for reason in reasons:
                        counts[reason] += 1
                        daily_exclusions[date][reason] += 1
                else:
                    if date not in ranges:
                        ranges[date] = [len(values['gross_bp']), len(values['gross_bp'])]
                    computed = spaces(Decimal(prev['m_text']), Decimal(prev['s_text']),
                                      Decimal(current['m_text']), Decimal(current['s_text']), fees)
                    for name, value in computed.items():
                        if value > 0:
                            positive_exact[name] += 1
                            daily_positive_exact[date][name] += 1
                        v = float(value)
                        if not math.isfinite(v) or v < 0:
                            raise ArithmeticError('Nonfinite/negative diagnostic scalar')
                        values[name].append(v)
                    ranges[date][1] += 1
                    counts['eligible_pairs'] += 1
            prev = current
            if n % 25000 == 0:
                save('progress.json', {'stage': 'pass2_diagnostic', 'rows': n, 'utc': utc(), 'pid': os.getpid()})
    if counts['eligible_pairs'] != qc['counts'].get('eligible_pairs', 0):
        raise ValueError('Pass1/pass2 eligibility mismatch')
    if config['_last_stream_integrity'] != qc['member_integrity']:
        raise ValueError('Decoded member identity changed between passes')
    summaries = {}
    per_day = {d: {'metrics': {}, 'exclusion_reasons_overlapping': dict(daily_exclusions[d]),
                   'QC': qc['daily'][d]} for d in qc['daily']}
    for name in names:
        summaries[name] = quantile_summary(values[name])
        summaries[name]['positive'] = positive_exact[name]
        summaries[name]['zero'] = len(values[name]) - positive_exact[name]
        summaries[name]['positive_fraction'] = positive_exact[name] / len(values[name]) if values[name] else None
        for date in per_day:
            a, b = ranges.get(date, [0, 0])
            per_day[date]['metrics'][name] = quantile_summary(values[name][a:b])
            stat = per_day[date]['metrics'][name]
            stat['positive'] = daily_positive_exact[date][name]
            stat['zero'] = stat['n'] - stat['positive']
            stat['positive_fraction'] = stat['positive'] / stat['n'] if stat['n'] else None
    if identity(path) != zip_id:
        raise ValueError('Archive changed after pass2')
    gross = summaries['gross_bp']
    classification = ('DATA_INSUFFICIENT' if gross['n'] == 0 else
                      'MODELED_SPACE_EXISTS_RESEARCH_ONLY' if gross['positive'] else
                      'NO_MODELED_ONE_SECOND_ACTIVE_SPACE')
    result = {'classification': classification, 'finished_utc': utc(), 'all_scenarios': summaries,
              'daily': per_day, 'counts': dict(counts), 'date_assignment': 'starting observation UTC date',
              'archive_before_and_after': zip_id, 'second_pass_EOF_and_CRC': True,
              'member_integrity': config['_last_stream_integrity'], 'positive_zero_counting': 'Decimal precision80 before float display conversion',
              'quantile_method': 'Exact Type7 on array(d), zeros included; fsum mean',
              'fees_per_leg_bp': fees,
              'limits': ['Ideal sampled quote envelope, not a signal or executable oracle strategy.',
                  'No actual account fee, dollar position, executable1BTC, wealth return or capacity claim.',
                  'Short direction ignores financing/borrow access; event arrival/age remains unknown.',
                  'Only adjacent exact1s observations, not all events/horizons/strategies.'],
              'actual_model_effort': 'UNKNOWN', 'models_or_trades': 0}
    save('diagnostic-results.json', result)
    save('result-seal.json', {'utc': utc(), 'results': {str(HERE / 'diagnostic-results.json'):
                             identity(HERE / 'diagnostic-results.json')}, 'archive': {str(path): zip_id}})
    return classification


def run(config, approval):
    gate = json.loads(Path(approval).read_text())
    if gate.get('allow_formal_run') is not True:
        raise ValueError('Explicit allow_formal_run gate required')
    verify(gate['source_inputs'])
    required = [str(HERE / n) for n in ['diagnostic.py', 'supervise.py', 'config.json', 'preflight.json']]
    if any(p not in gate['source_inputs'] for p in required):
        raise ValueError('Gate must bind source/config/preflight')
    verify(config['frozen_inputs'])
    auth = json.loads(Path(config['authorization']).read_text())
    if not auth['user_authorized'] or dt.datetime.now(dt.timezone.utc) >= dt.datetime.fromisoformat(auth['hard_deadline_utc']):
        raise ValueError('Authorization/deadline invalid')
    with (HERE / 'formal-started.lock').open('x') as f:
        json.dump({'utc': utc(), 'pid': os.getpid(), 'approval': str(Path(approval).resolve()),
                   'approval_identity': identity(approval), 'attempt': 1}, f)
    save('formal-input-seal.json', {'utc': utc(), 'source_inputs': gate['source_inputs'],
                                  'frozen_inputs': config['frozen_inputs'], 'config': config})
    path, zip_id = archive_download(config)
    qc = pass1(path, config, zip_id)
    # pass1 locals, including duplicate hash sets and distance arrays, are released on return.
    return pass2(path, config, qc, zip_id)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['prepare', 'run'])
    parser.add_argument('--approval')
    args = parser.parse_args()
    start = time.monotonic()
    config = json.loads((HERE / 'config.json').read_text())
    try:
        status = preflight(config) if args.stage == 'prepare' else run(config, args.approval)
        save('worker-' + args.stage + '-receipt.json', {'status': status, 'utc': utc(), 'pid': os.getpid(),
             'seconds': time.monotonic() - start, 'ru_maxrss_bytes_macos': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        print(json.dumps({'status': status, 'stage': args.stage}), flush=True)
    except Exception as e:
        # Never echo urllib signed redirect URLs, credentials or response bodies into errors.
        message = re.sub(r'(https?://[^\s?]+)\?[^\s]+', r'\1?[REDACTED]', str(e))
        save('worker-' + args.stage + '-failure.json', {'status': 'STOPPED_NO_RETRY', 'utc': utc(),
             'error_type': type(e).__name__, 'message': message, 'seconds': time.monotonic() - start})
        print(json.dumps({'status': 'STOPPED_NO_RETRY', 'error_type': type(e).__name__}), flush=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
