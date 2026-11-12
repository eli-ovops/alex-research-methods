"""One sealed future-endpoint observation from a stale known snapshot.

No trading or training. Past intermediate bars are not prospective targets.
No actual observations later than the retained input snapshot are read.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import random
import time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'endpoint-observation-20261015'


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, obj):
    if path.exists():
        raise RuntimeError('Refuse to replace existing observation artifact: ' + str(path))
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def main():
    # An attempted generation consumes this observation, including failed runs.
    # The calling parent additionally enforces a 300-second process timeout.
    dump(OUT / 'attempt.json', {
        'attempt_started_at_utc': now(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'policy': 'one attempted generation; retain marker on every failure; no automatic retry',
    })
    # Reuse audited offline loader; importing it does not import/run the model.
    import evaluate_kronos as base
    base.forbid_network()
    import numpy as np
    import pandas as pd
    import torch

    p = json.loads((OUT / 'protocol.json').read_text())
    if (OUT / 'observation.json').exists():
        raise RuntimeError('Observation already exists; no rerun')
    source_protocol = json.loads((ROOT / 'protocol.json').read_text())
    for key in ['model', 'tokenizer', 'sampling', 'features', 'context', 'horizon']:
        assert p[key] == source_protocol[key], key
    hashes = {}
    paths = {
        'data': ROOT / 'data/hourly.parquet',
        'model_weights': ROOT / 'weights/small/model.safetensors',
        'tokenizer_weights': ROOT / 'weights/tokenizer/model.safetensors',
        'model_config': ROOT / 'weights/small/config.json',
        'tokenizer_config': ROOT / 'weights/tokenizer/config.json',
    }
    for k, path in paths.items():
        hashes[k] = base.file_hash(path)
    assert hashes['data'] == p['dataset_sha256']
    assert hashes['model_weights'] == p['model']['weights_sha256']
    assert hashes['tokenizer_weights'] == p['tokenizer']['weights_sha256']
    prior = json.loads((ROOT / 'results/metadata.json').read_text())['identity']['hashes']
    for rel, h in prior['source_files'].items():
        assert base.file_hash(ROOT / 'vendor/Kronos' / rel) == h
    assert base.file_hash(ROOT / 'evaluate_kronos.py') == prior['harness_sha256']
    assert hashes['model_config'] == prior['model_config']
    assert hashes['tokenizer_config'] == prior['tokenizer_config']

    data = pd.read_parquet(paths['data'], columns=['symbol', 'datetime'] + p['features'])
    hist = data[data.symbol == p['symbol']].sort_values('datetime').set_index('datetime').tail(80)
    assert len(hist) == 80 and not hist.index.has_duplicates
    assert base.input_hash(hist) == p['input_sha256']
    future = pd.DatetimeIndex(pd.to_datetime(p['target_starts'], utc=True)).tz_convert(p['timezone'])
    assert len(future) == p['horizon'] == 12
    assert hist.index[-1].isoformat() == p['input_last_bar_start']
    assert p['snapshot_received_at_utc'] < p['frozen_at_utc']
    current = pd.Timestamp.now(tz='UTC')
    assert current < pd.Timestamp(p['terminal_bar_start']).tz_convert('UTC')
    assert np.isfinite(hist[p['features']].values).all()

    torch.set_num_threads(6)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    predictor = base.local_predictor(ROOT / 'vendor/Kronos', paths, source_protocol, torch)
    random.seed(p['seed'])
    np.random.seed(p['seed'])
    torch.manual_seed(p['seed'])
    started = now()
    t0 = time.perf_counter()
    with torch.inference_mode():
        result = predictor.predict(
            df=hist[p['features']].copy(), x_timestamp=pd.Series(hist.index),
            y_timestamp=pd.Series(future), pred_len=12,
            T=p['sampling']['T'], top_p=p['sampling']['top_p'],
            top_k=p['sampling']['top_k'], sample_count=p['sampling']['sample_count'],
            verbose=False,
        )
    finished = now()
    assert pd.Timestamp(finished) < pd.Timestamp(p['terminal_bar_start']).tz_convert('UTC')
    values = result[p['features']].to_numpy(float)
    assert values.shape == (12, 4) and np.isfinite(values).all()
    p0 = float(hist.iloc[-1]['close'])
    record = {
        'scope': p['scope'], 'status': 'sealed_pending_future_endpoint',
        'protocol_sha256': base.file_hash(OUT / 'protocol.json'),
        'runner_sha256': base.file_hash(Path(__file__)),
        'input_sha256': base.input_hash(hist), 'artifact_hashes': hashes,
        'prediction_started_at_utc': started, 'prediction_finished_at_utc': finished,
        'elapsed_seconds': time.perf_counter() - t0,
        'device': 'cpu', 'threads': 6,
        'model_training': predictor.model.training, 'tokenizer_training': predictor.tokenizer.training,
        'seed': p['seed'], 'snapshot_received_at_utc': p['snapshot_received_at_utc'],
        'input_last_bar_start': p['input_last_bar_start'], 'input_last_bar_end': p['input_last_bar_end'],
        'snapshot_age_at_prediction_hours': (pd.Timestamp(started) - pd.Timestamp(p['input_last_bar_end'])).total_seconds() / 3600,
        'target_starts': p['target_starts'], 'target_ends': p['target_ends'],
        'already_ended_intermediate_bars': p['already_ended_intermediate_bars'],
        'prediction_12step_ohlc': values.tolist(), 'prediction_features': p['features'],
        'terminal_bar_start': p['terminal_bar_start'], 'terminal_bar_end': p['terminal_bar_end'],
        'p0_old_snapshot_close': p0, 'predicted_terminal_close': float(values[-1, 3]),
        'predicted_terminal_return_from_old_close': float(values[-1, 3] / p0 - 1),
        'predicted_nonpositive_values': int((values <= 0).sum()),
        'future_actual_price': None, 'score': None,
        'not_claimed': ['full 12-bar prospective path', 'return from current executable entry price',
                        'incremental predictive advantage', 'profitability', 'capacity', 'wealth completion'],
    }
    record['record_sha256'] = base.digest_obj(record)
    dump(OUT / 'observation.json', record)
    assert pd.Timestamp.now(tz='UTC') < pd.Timestamp(p['terminal_bar_start']).tz_convert('UTC')
    dump(OUT / 'seal-receipt.json', {
        'sealed_at_utc': now(), 'observation_file_sha256': base.file_hash(OUT / 'observation.json'),
        'before_terminal_bar_start': True,
        'scope': 'local file seal only; no external trusted timestamp authority',
    })
    print(json.dumps({k: record[k] for k in ['status', 'prediction_finished_at_utc',
        'predicted_terminal_close', 'terminal_bar_start', 'terminal_bar_end', 'elapsed_seconds']}))


if __name__ == '__main__':
    main()
