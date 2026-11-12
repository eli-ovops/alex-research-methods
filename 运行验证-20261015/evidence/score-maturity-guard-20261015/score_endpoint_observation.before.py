"""Score the retained single endpoint only after maturity; never runs a model."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'endpoint-observation-20261015'


def digest(obj):
    b = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(b).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--receipt', type=Path)
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
    if args.data is None or args.receipt is None:
        print(json.dumps({'status': 'AWAIT_SAME_PROVIDER_TARGET_DATA', 'score_created': False,
                          'model_executed': False}))
        return
    receipt = json.loads(args.receipt.read_text())
    h = hashlib.sha256(args.data.read_bytes()).hexdigest()
    assert h == receipt['sha256']
    assert receipt['dataset_id'] == 'twelvedata/financial-world-model'
    assert receipt['relative_file'] == 'bars_1h/test.parquet'
    assert len(receipt['dataset_revision']) == 40
    expected_url = ('https://huggingface.co/datasets/twelvedata/financial-world-model/resolve/'
                    + receipt['dataset_revision'] + '/bars_1h/test.parquet')
    assert receipt['source_url'] == expected_url
    assert datetime.fromisoformat(receipt['retrieved_at_utc']) >= target_end
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
