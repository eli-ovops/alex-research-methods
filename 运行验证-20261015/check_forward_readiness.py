"""Read-only temporal readiness check; does not import or execute a model."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

import numpy as np
import pandas as pd
import exchange_calendars as xcals

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'evidence/prospective-readiness-20261015'


def main():
    p = json.loads((ROOT / 'protocol.json').read_text())
    rule = json.loads((OUT / 'readiness-rule.json').read_text())
    meta = json.loads((OUT / 'metadata-receipt.json').read_text())
    assert rule['context'] == p['context'] == 80
    assert rule['horizon'] == p['horizon'] == 12
    assert rule['features'] == p['features']
    assert rule['model'] == p['model']
    assert rule['sampling'] == p['sampling']
    now = pd.Timestamp.now(tz='UTC')
    file = ROOT / 'data/hourly.parquet'
    data = pd.read_parquet(file, columns=['symbol', 'datetime'] + p['features'])
    data = data[data.symbol == 'AAPL'].sort_values('datetime').set_index('datetime')
    last = data.index[-1]
    start = data.tail(80).index[0].date()
    stop = (last + pd.Timedelta(days=18)).date()
    cal = xcals.get_calendar('XNYS', start=start, end=stop)
    starts, ends = [], []
    # Use the calendar's actual sessions; requested end can be a weekend.
    for day in cal.sessions:
        op = cal.session_open(day).tz_convert('America/New_York')
        cl = cal.session_close(day).tz_convert('America/New_York')
        for ts in pd.date_range(op, cl, freq='h', inclusive='left'):
            starts.append(ts)
            ends.append(min(ts + pd.Timedelta(hours=1), cl))
    grid, endgrid = pd.DatetimeIndex(starts), pd.DatetimeIndex(ends)
    pos = grid.get_loc(last)
    actual_hist = data.tail(80)
    expected_hist = grid[pos - 79:pos + 1]
    future = grid[pos + 1:pos + 13]
    future_ends = endgrid[pos + 1:pos + 13]
    consecutive = (len(actual_hist) == len(expected_hist) == 80
                   and bool((actual_hist.index == expected_hist).all()))
    all_complete = bool((endgrid[pos - 79:pos + 1].tz_convert('UTC') <= now).all())
    values = actual_hist[p['features']].to_numpy(float)
    valid = bool(np.isfinite(values).all() and (values > 0).all())
    started = int((future.tz_convert('UTC') <= now).sum())
    ended = int((future_ends.tz_convert('UTC') <= now).sum())
    h = hashlib.sha256(file.read_bytes()).hexdigest()
    source = next(x for x in meta['selected_files'] if x['rfilename'] == 'bars_1h/test.parquet')
    file_matches = h == source['lfs']['sha256']
    reasons = []
    if started:
        reasons.append('next consecutive target bars already began')
    if not consecutive:
        reasons.append('history not exactly 80 consecutive calendar bars')
    if not all_complete or not valid:
        reasons.append('input incomplete or invalid')
    if len(future) != 12 or not file_matches:
        reasons.append('future calendar coverage or current snapshot identity mismatch')
    result = {
        'checked_at_utc': now.isoformat(),
        'source_metadata_checked_at_utc': meta['retrieved_at_utc'],
        'status': 'READY' if not reasons else 'STOP_CURRENT_PROSPECTIVE_WINDOW',
        'stop_reasons': reasons,
        'dataset_revision_current_at_metadata_check': meta['current_revision'],
        'same_revision_as_initial': meta['current_revision'] == p['dataset']['revision'],
        'current_file_sha256': h,
        'file_matches_current_lfs': file_matches,
        'input_rows': len(actual_hist),
        'input_first': actual_hist.index[0].isoformat(),
        'input_last_bar_start': last.isoformat(),
        'input_last_bar_end': endgrid[pos].isoformat(),
        'input_consecutive_calendar': consecutive,
        'input_all_complete': all_complete,
        'input_all_finite_positive': valid,
        'target_starts': [x.isoformat() for x in future],
        'target_ends': [x.isoformat() for x in future_ends],
        'targets_already_begun': started,
        'targets_already_ended': ended,
        'targets_remaining_future': len(future) - started,
        'new_model_executions': 0,
        'next_safe_action': 'newer public snapshot then same readiness rule; no skipping elapsed targets or padding missing input',
    }
    (OUT / 'readiness.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
