"""Score the retained single endpoint only after maturity; never runs a model."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'endpoint-observation-20261015'


def digest(obj):
    b = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(b).hexdigest()


class CompletionEvidencePending(ValueError):
    """No acceptable local evidence of a completed target is available."""


def aware_time(value):
    if not isinstance(value, str):
        raise CompletionEvidencePending('Missing timestamp')
    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if value.tzinfo is None or value.utcoffset() is None:
        raise CompletionEvidencePending('Timestamp has no timezone; do not guess')
    return value.astimezone(timezone.utc)


def check_source(source, package_dir):
    """Check local original bytes, not the truth of the source's contents."""
    url = urlparse(source['source_url'])
    if url.scheme != 'https' or not url.hostname or url.username or url.password:
        raise CompletionEvidencePending('Missing public HTTPS source URL')
    path = Path(source['artifact_path'])
    if not path.is_absolute():
        path = package_dir / path
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['artifact_sha256']:
        raise CompletionEvidencePending('Source original missing or hash mismatch')


def validate_completion(package, receipt, obs, data_sha256, package_dir, checked_at):
    """Consistency/time/original-file guard only; independent content review is required.

    A repository lastModified, download time, successor bar, or a boolean claim
    alone is not completion evidence. This function cannot authenticate reviewers
    or establish that their substantive interpretation of originals is correct.
    """
    expected = {
        'dataset_id': 'twelvedata/financial-world-model',
        'dataset_revision': receipt['dataset_revision'],
        'relative_file': 'bars_1h/test.parquet', 'data_sha256': data_sha256,
        'symbol': 'AAPL', 'timeframe': '1h',
        'target_bar_start': obs['terminal_bar_start'],
        'target_bar_end': obs['terminal_bar_end'],
    }
    if any(package.get(k) != v for k, v in expected.items()):
        raise CompletionEvidencePending('Completion package does not bind exact file/revision/hash/target')
    target_end = aware_time(obs['terminal_bar_end'])
    aware_time(package['target_bar_start'])
    pub = package['file_publication']
    published = aware_time(pub['event_at_utc'])
    completion = package['completion']
    event = aware_time(completion['event_at_utc'])
    if completion['type'] not in {'post_end_source_fetch', 'post_end_generation', 'official_completed_bar'}:
        raise CompletionEvidencePending('Unsupported completion evidence type')
    received = aware_time(receipt['retrieved_at_utc'])
    review = package['independent_review']
    reviewed = aware_time(review['reviewed_at_utc'])
    if not (target_end <= event <= published <= received <= checked_at and published <= reviewed <= checked_at):
        raise CompletionEvidencePending('File/event/review predates completion or is future-dated')
    check_source(pub, package_dir)
    check_source(completion, package_dir)
    if (not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip()
            or review.get('decision') != 'accepted'
            or not isinstance(review.get('source_content_finding'), str)
            or not review['source_content_finding'].strip()
            or review['source_content_finding'].strip().lower() in {'true', 'yes', 'ok', 'accepted', 'approved'}):
        raise CompletionEvidencePending('Independent reviewer and substantive source finding required')
    payload = {k: v for k, v in package.items() if k != 'independent_review'}
    if review.get('reviewed_payload_sha256') != digest(payload):
        raise CompletionEvidencePending('Review does not bind this evidence package')
    return {'machine_check': 'consistency_only', 'reviewer': review['reviewer'],
            'reviewed_at_utc': review['reviewed_at_utc'],
            'limit': 'Source content must have been independently verified; machine checks do not prove completion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--completion-evidence', type=Path)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    raw = (OUT / 'observation.json').read_bytes()
    obs = json.loads(raw)
    seal = json.loads((OUT / 'seal-receipt.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == seal['observation_file_sha256']
    record_checksum = obs.pop('record_sha256')
    assert digest(obs) == record_checksum
    assert obs['future_actual_price'] is None and obs['score'] is None
    target_end = datetime.fromisoformat(obs['terminal_bar_end'])
    if now < target_end:
        print(json.dumps({'checked_at_utc': now.isoformat(), 'status': 'NOT_MATURED',
            'target_end': obs['terminal_bar_end'], 'score_created': False, 'model_executed': False}))
        return
    if (OUT / 'score.json').exists():
        raise RuntimeError('A first score already exists; do not overwrite or selectively replace it')
    try:
        if args.data is None or args.receipt is None or args.completion_evidence is None:
            raise CompletionEvidencePending('Data, receipt and reviewed completion evidence required')
        receipt = json.loads(args.receipt.read_text())
        h = hashlib.sha256(args.data.read_bytes()).hexdigest()
        if (h != receipt['sha256'] or receipt['dataset_id'] != 'twelvedata/financial-world-model'
                or receipt['relative_file'] != 'bars_1h/test.parquet'
                or len(receipt['dataset_revision']) != 40
                or any(c not in '0123456789abcdef' for c in receipt['dataset_revision'])):
            raise CompletionEvidencePending('Data receipt identity/hash mismatch')
        expected_url = ('https://huggingface.co/datasets/twelvedata/financial-world-model/resolve/'
                        + receipt['dataset_revision'] + '/bars_1h/test.parquet')
        if receipt['source_url'] != expected_url:
            raise CompletionEvidencePending('Receipt URL does not bind selected revision/file')
        completion = json.loads(args.completion_evidence.read_text())
        guard = validate_completion(completion, receipt, obs, h, args.completion_evidence.resolve().parent, now)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'checked_at_utc': now.isoformat(), 'status': 'AWAIT_COMPLETED_TARGET_EVIDENCE',
                          'reason': str(exc), 'score_created': False, 'model_executed': False}))
        return
    import pandas as pd
    import numpy as np
    data = pd.read_parquet(args.data, columns=['symbol', 'datetime', 'timeframe', 'close'])
    ts = pd.to_datetime(data['datetime'], errors='raise')
    if ts.dt.tz is None:
        raise RuntimeError('Source time zone is missing; do not guess')
    target_start = pd.Timestamp(obs['terminal_bar_start'])
    rows = data.loc[(data.symbol == 'AAPL') & (ts == target_start)]
    if len(rows) != 1:
        print(json.dumps({'status': 'TARGET_MISSING_OR_DUPLICATED', 'matching_rows': len(rows),
                          'score_created': False, 'model_executed': False}))
        return
    actual = float(rows.iloc[0]['close'])
    assert rows.iloc[0]['timeframe'] == '1h'
    assert np.isfinite(actual) and actual > 0
    p0 = obs['p0_old_snapshot_close']
    r = actual / p0 - 1
    rh = obs['predicted_terminal_return_from_old_close']
    zse, mse = r * r, (rh - r) ** 2
    score = {
        'scored_at_utc': now.isoformat(), 'n': 1,
        'scope': 'one stale-snapshot future-endpoint observation; not investment performance',
        'observation_file_sha256': seal['observation_file_sha256'],
        'target_bar_start': obs['terminal_bar_start'], 'target_bar_end': obs['terminal_bar_end'],
        'data_receipt': receipt, 'actual_terminal_close': actual,
        'completion_evidence': completion,
        'completion_evidence_sha256': hashlib.sha256(args.completion_evidence.read_bytes()).hexdigest(),
        'completion_guard': guard,
        'predicted_terminal_close': obs['predicted_terminal_close'],
        'r_from_old_snapshot_close': r, 'r_hat_from_old_snapshot_close': rh,
        'zero_squared_error': zse, 'model_squared_error': mse, 'd': zse - mse,
        'advantage_gate': 'UNDETERMINED_N1', 'profit_tested': False,
        'must_not_pool_with_original188': True,
        'baseline_limit': 'old snapshot close is not the latest known market price or an executable entry price',
    }
    benchmark_path = OUT / 'secondary-benchmark-before-outcome.json'
    if benchmark_path.exists():
        benchmark = json.loads(benchmark_path.read_text())
        assert datetime.fromisoformat(benchmark['frozen_at_utc']) < datetime.fromisoformat(obs['terminal_bar_start'])
        latest = float(benchmark['latest_regular_close_USD'])
        benchmark_r = latest / p0 - 1
        score['descriptive_secondary_latest_close'] = {
            'benchmark_file_sha256': hashlib.sha256(benchmark_path.read_bytes()).hexdigest(),
            'latest_close_USD': latest,
            'squared_error_same_old_close_scale': (benchmark_r - r) ** 2,
            'model_squared_error_minus_secondary': mse - (benchmark_r - r) ** 2,
            'interpretation': 'n=1, post-model pre-outcome exploratory comparison; no efficacy verdict',
        }
    with (OUT / 'score.json').open('x', encoding='utf-8') as f:
        json.dump(score, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({'status': 'SINGLE_ENDPOINT_SCORED_NO_EFFICACY_VERDICT', 'n': 1,
                      'd': zse - mse, 'profit_tested': False}))


if __name__ == '__main__':
    main()
