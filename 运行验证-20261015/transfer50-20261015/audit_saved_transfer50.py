#!/usr/bin/env python3
"""Independently rebuild completed saved forecasts against the fixed source data.

Never imports the model or the assessment adapter. Does not audit a partial run.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def require(condition, description):
    if not condition:
        raise ValueError(description)


def ready(run):
    required = [run/'launch-attempt.json', run/'results/state.json', run/'results/summary.json']
    if not all(path.is_file() for path in required):
        return False
    launch, state, summary = [read(path) for path in required]
    return (launch.get('status') == 'CHILD_EXITED' and launch.get('child_exit_code') == 0
            and state.get('status') == 'completed' and summary.get('complete_panel') is True)


def audit(run):
    # No model, market-data or score read occurs before this completion guard.
    if not ready(run):
        launch_path = run/'launch-attempt.json'
        terminal = (launch_path.is_file() and read(launch_path).get('status') in
                    {'CHILD_EXITED','DEADLINE_STOP','INTERRUPTED','LAUNCHER_ERROR'})
        print(json.dumps({'status':'INCOMPLETE_RUN_NOT_AUDITED' if terminal else 'AWAIT_COMPLETED_RUN', 'model_runs':0,
                          'audit_written':False, 'scope':'no claim that a process is live'}))
        return 4 if terminal else 3
    import numpy as np
    import pandas as pd
    import exchange_calendars as xcals

    base, out = run.parent, run/'results'
    protocol, freeze = read(run/'protocol.json'), read(run/'freeze-receipt.json')
    summary, state, runtime = read(out/'summary.json'), read(out/'state.json'), read(out/'runtime.json')
    launch, metadata = read(run/'launch-attempt.json'), read(out/'metadata.json')
    identity = metadata['identity']
    checks = {}
    for name, expected in [('evaluate_transfer50.py',protocol['adapter_sha256']),
                           ('launch_transfer50.py',protocol['launcher_sha256'])]:
        require(sha(run/name) == expected, 'Frozen execution code changed: '+name)
    require(sha(base/'evaluate_kronos.py') == protocol['helper_sha256'], 'Helper changed')
    require(sha(run/'protocol.json') == freeze['protocol_file_sha256'], 'Protocol differs from freeze')
    require(sha(run/'authorization.json') == protocol['authorization_receipt_sha256'], 'Authorization receipt changed')
    require(identity['protocol'] == protocol and identity['protocol_file_sha256'] == freeze['protocol_file_sha256'],
            'Run metadata is not the frozen protocol')
    require(identity['protocol_sha256'] == digest(protocol), 'Canonical protocol identity mismatch')
    require(identity['mode'] == 'one_attempt_transfer50', 'Incorrect run identity mode')
    checks['frozen_code_protocol_authorization_identity'] = True

    artifacts = {'data':base/'data/hourly.parquet',
                 'model_weights':base/'weights/small/model.safetensors',
                 'tokenizer_weights':base/'weights/tokenizer/model.safetensors',
                 'model_config':base/'weights/small/config.json',
                 'tokenizer_config':base/'weights/tokenizer/config.json'}
    expected = {'data':protocol['dataset']['sha256'],
                'model_weights':protocol['model']['weights_sha256'],
                'tokenizer_weights':protocol['tokenizer']['weights_sha256'],
                'model_config':protocol['model_config_sha256'],
                'tokenizer_config':protocol['tokenizer_config_sha256']}
    for name, path in artifacts.items():
        require(sha(path) == expected[name] == identity['hashes'][name], 'Artifact changed: '+name)
    source_hashes = {name:sha(base/'vendor/Kronos'/name) for name in protocol['source_files_sha256']}
    require(source_hashes == protocol['source_files_sha256'] and digest(source_hashes) == protocol['source_tree_sha256'],
            'Official source differs from frozen files')
    checks['all_source_weights_configs_data_hashes'] = True
    proposal = read(base/'evidence/reuse-readiness-20261015/fixed-transfer-screen-proposal.json')
    for name, expected_hash in proposal['preserved_original_sha256'].items():
        require(sha(base/name) == expected_hash, 'Old protected artifact changed: '+name)
    checks['old_188_and_sealed_AAPL_preserved'] = True

    features = ['open','high','low','close']
    raw = pd.read_parquet(artifacts['data'], columns=['symbol','datetime']+features)
    symbols = protocol['symbols']
    require(len(symbols) == len(set(symbols)) == 50 and 'AAPL' not in symbols, 'Incorrect symbol set')
    frames = {s:raw.loc[raw.symbol==s, ['datetime']+features].set_index('datetime') for s in symbols}
    first = min(frame.index.min() for frame in frames.values())
    last = max(frame.index.max() for frame in frames.values())
    calendar = xcals.get_calendar('XNYS', start=first.date().isoformat(), end=last.date().isoformat())
    starts, ends = [], []
    for session in calendar.sessions_in_range(first.date().isoformat(),last.date().isoformat()):
        op = pd.Timestamp(calendar.session_open(session)).tz_convert(protocol['timezone'])
        cl = pd.Timestamp(calendar.session_close(session)).tz_convert(protocol['timezone'])
        for stamp in pd.date_range(op,cl,freq='h',inclusive='left'):
            starts.append(stamp)
            ends.append(min(stamp+pd.Timedelta(hours=1),cl))
    grid = pd.DatetimeIndex(starts)
    last_position = int(grid.get_indexer([last])[0])
    require(last_position >= 0, 'Final raw timestamp absent from calendar')
    grid, ends = grid[:last_position+1], ends[:last_position+1]
    for symbol, frame in frames.items():
        require(len(frame)==len(grid) and np.all(frame.index==grid), 'Calendar mismatch: '+symbol)
        values = frame[features].to_numpy(dtype='float64')
        require(np.isfinite(values).all() and (values>0).all(), 'Invalid source OHLC: '+symbol)
    threshold = pd.Timestamp(protocol['start_date'],tz=protocol['timezone'])
    first_anchor = max(protocol['context']-1,int(grid.searchsorted(threshold))-1)
    anchors = list(range(first_anchor,len(grid)-protocol['horizon'],protocol['stride']))
    require(len(anchors)==protocol['expected_time_windows']==188, 'Incorrect independently rebuilt windows')
    checks['independent_calendar_and_complete_common_grid'] = True

    records = [json.loads(line) for line in (out/'predictions.jsonl').read_text().splitlines() if line.strip()]
    require(len(records)==protocol['expected_records']==len(anchors)*len(symbols)==9400, 'Incomplete record count')
    actual = np.empty((len(anchors),len(symbols)))
    forecast = np.empty_like(actual)
    elapsed_sum = 0.0
    prior_finish = datetime.fromisoformat(runtime['started_at_utc'])
    frozen = datetime.fromisoformat(protocol['frozen_at_utc'])
    require(frozen < prior_finish, 'Model loaded before freeze')
    require(runtime['device']=='cpu' and runtime['torch_threads']==6 and runtime['torch_interop_threads']==1,
            'Runtime resource mismatch')
    require(runtime['model_training'] is False and runtime['tokenizer_training'] is False
            and runtime['new_training_steps']==0 and runtime['deterministic_algorithms'] is True,
            'Runtime not fixed eval-only inference')
    identity_sha = digest(identity)
    require(runtime['identity_sha256']==identity_sha, 'Runtime identity does not match run metadata')
    for index, row in enumerate(records):
        window, column = divmod(index,len(symbols))
        symbol, anchor = symbols[column], anchors[window]
        hist = grid[anchor-protocol['context']+1:anchor+1]
        future = grid[anchor+1:anchor+1+protocol['horizon']]
        unsigned = dict(row)
        checksum = unsigned.pop('record_sha256')
        require(checksum==digest(unsigned), f'Record checksum mismatch: {index}')
        require(row['symbol']==symbol and row['window_index']==window, f'Record order/identity mismatch: {index}')
        require(row['last_input']==hist[-1].isoformat() and row['target_timestamps']==[t.isoformat() for t in future],
                f'Record target calendar mismatch: {index}')
        require(row['forecast_origin_bar_end']==ends[anchor].isoformat(), f'Origin bar end mismatch: {index}')
        require(row['seed']==20261015+1000000*(column+1)+window, f'Seed mismatch: {index}')
        source = frames[symbol].loc[hist,features]
        input_digest = digest({'timestamps':[t.isoformat() for t in source.index],
                               'features':features,'values':source.values.tolist()})
        require(row['input_sha256']==input_digest and row['source_identity_sha256']==identity_sha,
                f'Input/source hash mismatch: {index}')
        p0, truth = float(source.iloc[-1]['close']), float(frames[symbol].loc[future[-1],'close'])
        require(row['p0']==p0 and row['actual_terminal_close']==truth, f'Source price endpoint mismatch: {index}')
        path = np.asarray(row['prediction_12step_ohlc'],dtype=float)
        require(path.shape==(12,4) and np.isfinite(path).all() and (path>0).all(), f'Invalid saved forecast: {index}')
        require(float(path[-1,3])==row['terminal_close_10sample_mean'], f'Saved path/terminal mismatch: {index}')
        r, rh = truth/p0-1, float(path[-1,3])/p0-1
        values = {'r':r,'r_hat':rh,'zero_squared_error':r*r,'model_squared_error':(rh-r)**2,'d':r*r-(rh-r)**2}
        require(all(math.isclose(row[k],v,rel_tol=1e-12,abs_tol=1e-15) for k,v in values.items()),
                f'Error arithmetic mismatch: {index}')
        begin = datetime.fromisoformat(row['prediction_started_at_utc'])
        finish = datetime.fromisoformat(row['prediction_finished_at_utc'])
        require(begin>=prior_finish and finish>=begin, f'Generation timestamp ordering mismatch: {index}')
        prior_finish = finish
        require(row['inference_seconds']>=0, f'Negative inference time: {index}')
        elapsed_sum += row['inference_seconds']
        require(math.isclose(row['cumulative_inference_seconds'],elapsed_sum,rel_tol=1e-10,abs_tol=1e-6),
                f'Cumulative inference time mismatch: {index}')
        actual[window,column], forecast[window,column] = r, rh
    checks.update(all_9400_record_identities_hashes=True, all_9400_source_history_input_hashes=True,
                  all_9400_source_p0_actual_endpoint_mappings=True, all_9400_saved_paths_and_error_arithmetic=True,
                  all_9400_seeds_and_generation_order=True)
    require(elapsed_sum<=14400 and launch['wall_seconds']<=14400 and state['cumulative_inference_seconds']<=14400,
            'Resource cap exceeded')
    require(math.isclose(elapsed_sum,state['cumulative_inference_seconds'],rel_tol=1e-10,abs_tol=1e-6),
            'Final inference time mismatch')
    require(state['predictions_sha256']==sha(out/'predictions.jsonl'), 'Final saved prediction checksum mismatch')
    require(read(out/'qc.json')['status']=='PASS', 'Actual QC was not PASS')
    require(state['records']==9400 and summary['n_records']==9400
            and summary['n_symbols']==50 and summary['n_complete_time_windows']==188
            and summary['planned_records']==9400 and summary['planned_time_windows']==188
            and summary['qc_status']=='PASS' and summary['termination'] is None
            and summary['bootstrap']==protocol['CI'], 'Reported completion counts or analysis settings mismatch')
    checks['actual_runtime_budget_and_terminal_complete_state'] = True

    zse, mse = actual**2, (forecast-actual)**2
    panel_d = zse-mse
    temporal_d = panel_d.mean(axis=1)
    n = len(temporal_d)
    split = n//2
    halves = [float(temporal_d[:split].mean()),float(temporal_d[split:].mean())]
    rng = np.random.default_rng(protocol['CI']['seed'])
    block = protocol['CI']['block_length']
    draws = []
    for _ in range(protocol['CI']['resamples']):
        starts = rng.integers(0,n,size=math.ceil(n/block))
        indexes = np.concatenate([(start+np.arange(block))%n for start in starts])[:n]
        draws.append(float(temporal_d[indexes].mean()))
    alpha = (1-protocol['CI']['confidence'])/2
    ci = np.quantile(draws,[alpha,1-alpha]).tolist()
    recomputed = {'zero_mse':float(zse.mean()),'model_mse':float(mse.mean()),
                  'paired_d_mean':float(temporal_d.mean()),
                  'relative_mse_improvement':float((zse.mean()-mse.mean())/zse.mean()),
                  'chronological_halves_mean_d':halves,'circular_block_bootstrap_95CI':ci}
    for name,value in recomputed.items():
        require(np.allclose(summary[name],value,rtol=1e-11,atol=1e-15), 'Summary statistic mismatch: '+name)
    passed = bool(ci[0]>0 and min(halves)>0)
    require(summary['gate_passed']==passed and state['gate_passed']==passed, 'Gate classification mismatch')
    require(summary['status']==('prediction_gate_pass' if passed else 'prediction_gate_not_passed'), 'Status mismatch')
    checks['independent_time_block_statistics_and_pass_gate'] = True
    per_symbol = read(out/'per-symbol-descriptive.json')
    require(set(per_symbol)==set(symbols), 'Saved descriptive symbol set mismatch')
    for column,symbol in enumerate(symbols):
        require(per_symbol[symbol]['n']==188 and per_symbol[symbol]['coverage']==1, 'Per-symbol coverage mismatch')
        for name,value in [('zero_mse',zse[:,column].mean()),('model_mse',mse[:,column].mean())]:
            require(math.isclose(per_symbol[symbol][name],float(value),rel_tol=1e-12,abs_tol=1e-15),
                    'Per-symbol metric mismatch: '+symbol)
        z, m = float(zse[:,column].mean()), float(mse[:,column].mean())
        ratio = (z-m)/z if z>0 else None
        saved_ratio = per_symbol[symbol]['relative_mse_improvement']
        require((ratio is None and saved_ratio is None) or
                (ratio is not None and saved_ratio is not None and
                 math.isclose(saved_ratio,ratio,rel_tol=1e-12,abs_tol=1e-15)),
                'Per-symbol relative improvement mismatch: '+symbol)
        require(per_symbol[symbol]['descriptive_only'] is True, 'Per-symbol descriptive label mismatch')
    saved_time = read(out/'time-window-means.json')
    saved_time_d = saved_time['rows']
    require(saved_time['cross_section_kept_together'] is True and
            [x['window_index'] for x in saved_time_d]==list(range(188)),
            'Saved time-window identity/cross-section declaration mismatch')
    require(len(saved_time_d)==188 and np.allclose([x['paired_d_mean'] for x in saved_time_d],temporal_d,rtol=1e-12,atol=1e-15),
            'Saved time aggregate mismatch')
    checks['all_symbol_descriptive_and_time_aggregate_values'] = True
    result = {'audited_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS',
              'scope':'independent completed saved-artifact source and statistics audit; no model rerun or trading',
              'audit_code_sha256':sha(__file__),'protocol_sha256':sha(run/'protocol.json'),
              'predictions_sha256':sha(out/'predictions.jsonl'),'checks':checks,
              'n_records':9400,'n_synchronous_time_windows':188,'n_symbols':50,
              'recomputed':recomputed,'prediction_gate_passed':passed,
              'per_symbol_lower_MSE_count_descriptive_only':int((panel_d.mean(axis=0)>0).sum()),
              'cumulative_inference_seconds':elapsed_sum,'parent_wall_seconds':launch['wall_seconds'],
              'new_model_runs':0,'profitability_established':False,
              'limits':summary['limits']}
    target = run/'independent-artifact-audit.json'
    with target.open('x') as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2,allow_nan=False)
        handle.write('\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(audit(Path(__file__).resolve().parent))
    except Exception as exc:
        print(json.dumps({'status':'AUDIT_NOT_PASSED','error':f'{type(exc).__name__}: {exc}',
                          'model_runs':0,'no_success_claim':True}),file=sys.stderr)
        raise SystemExit(2)
