"""Read-only verification of sealed original accounts; creates no strategy accounts."""
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
import csv, hashlib, io, json, math, statistics, time, resource

resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
START = time.monotonic()
BASE = Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015')
UNIT = BASE/'evidence/annual-common-inventory-2026-once-20261021'
E = UNIT/'execution-owner'
OUT = UNIT/'independent-review'
identities = {}
residuals = {}
checks = 0

def blob(path):
    path = Path(path)
    assert path.resolve().is_relative_to(BASE.resolve())
    b = path.read_bytes()
    identities[str(path)] = {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
    return b

def js(path):
    return json.loads(blob(path))

def bind(meta):
    b = blob(meta['path'])
    assert len(b) == meta['bytes']
    assert hashlib.sha256(b).hexdigest() == meta['sha256']

def near(a, b, category, weight=False):
    global checks
    assert math.isfinite(a) and math.isfinite(b), (category, 'NONFINITE')
    err = abs(a-b)
    residuals[category] = max(residuals.get(category, 0.), err)
    tolerance = 1e-8 if weight else max(1e-8, 1e-10*max(abs(a), abs(b), 1.))
    assert err <= tolerance, (category, a, b, err, tolerance)
    checks += 1

def stamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

cfg = js(E/'config.json')
final = js(E/'final-result-seal.json')
for field in ('result', 'six_ledgers', 'target', 'common_seed'):
    bind(final[field])
sealed = js(E/'all-six-ledgers-seal.json')
for meta in list(sealed['ledgers'].values()) + [sealed['target'], sealed['common_seed'], sealed['code']]:
    bind(meta)
for meta in sealed['inputs_rechecked'].values():
    bind(meta)
target = js(E/'target-before-market-seal.json')
common = js(E/'common-seed-and-market-inputs.json')
result = js(E/'results.json')
receipt = js(E/'formal-command-receipt.json')
gate = js(UNIT/'root/once-formal-release-gate.json')
pre = js(E/'pre-market-seal.json')
started = js(E/'formal-started.json')
wrapper_started = js(E/'formal-command-started.json')
preparation_manifest = js(E/'preparation-manifest.json')
for meta in preparation_manifest['files']:
    bind(meta)
for field in ('code', 'config', 'gate', 'preflight'):
    bind(pre[field])
for field in ('manifest', 'review', 'supervisor', 'authorization'):
    bind(gate[field])
bind(started['gate'])
for field in ('stdout', 'stderr'):
    bind(receipt[field])
assert receipt['exit_code'] == 0 and receipt['resource_stop'] is None
assert receipt['stdout']['bytes'] == receipt['stderr']['bytes'] == 0
assert final['formal_attempts'] == started['formal_attempts'] == receipt['formal_attempts'] == result['formal_attempts'] == 1
assert gate['status'] == 'RELEASED_ONCE_COMMON_INVENTORY_2026'
assert gate['code_sha256'] == pre['code']['sha256']
assert gate['config_sha256'] == pre['config']['sha256']
timeline = [gate['released_UTC'], wrapper_started['UTC'], started['UTC'], pre['UTC'], target['UTC'], common['UTC'], sealed['UTC'], result['UTC'], final['UTC'], receipt['UTC_end']]
assert all(stamp(a) <= stamp(b) for a, b in zip(timeline, timeline[1:]))
assert stamp(receipt['UTC_end']) < stamp(cfg['work_deadline_UTC'])
assert sealed['all_six_sealed_before_scoring'] is True
assert target['2026_prices_not_yet_parsed'] is True
assert len(target['warmup_dates']) == 61
assert target['warmup_dates'] == [(date(2025, 10, 31)+timedelta(days=i)).isoformat() for i in range(61)]
assert target['information_cutoff'] == '2025-12-30=e-2'
near(result['A_f2026'], target['A_f2026'], 'frozen_target', True)
near(result['C_k'], cfg['fixed_k'], 'fixed_C_target', True)

points = common['points']
assert len(points) == 289
expected_dates = [(date(2026, 1, 1)+timedelta(days=i)).isoformat() for i in range(289)]
assert [p['date'] for p in points] == expected_dates and expected_dates[-1] == '2026-10-16'
assert points[0]['volume'] > 0 and points[-1]['volume'] > 0
# Source-to-sealed-point verification only: no signal or strategy is computed.
source_points = []
for r in csv.DictReader(io.StringIO(blob(cfg['inputs']['daily']['path']).decode())):
    if '2026-01-01' <= r['date'] <= '2026-10-16':
        source_points.append({'date': r['date'], 'price': float(r['price']), 'volume': float(r['volume'])})
assert source_points == points
q0, c0 = float(cfg['seed']['units']), float(cfg['seed']['cash'])
near(common['scale']*(q0*points[0]['price']+c0), 5000., 'common_scale')
near(common['units'], q0*common['scale'], 'scaled_units')
near(common['cash'], c0*common['scale'], 'scaled_cash')
near(common['units']*points[0]['price']+common['cash'], 5000., 'initial_equity')

metrics = {}
row_count = 0
for key, meta in sealed['ledgers'].items():
    group, cost = key.split('-')
    fee = int(cost)/10000
    rows = list(csv.DictReader(io.StringIO(blob(meta['path']).decode())))
    assert len(rows) == 289
    row_count += len(rows)
    returns, fees, notionals, exposures, marks = [], [], [], [], []
    previous = None
    for i, r in enumerate(rows):
        assert r['date'] == expected_dates[i] and r['decision_UTC'] == expected_dates[i]+'T00:10:00Z'
        assert r['group'] == group
        n = {k: float(r[k]) for k in ('fee_rate','price','volume','pretrade_cash','pretrade_units','pretrade_equity','pretrade_exposure','posttrade_cash','posttrade_units','posttrade_equity','posttrade_exposure','signed_nominal_USD','fee_USD')}
        assert all(math.isfinite(v) for v in n.values())
        assert min(n['pretrade_cash'], n['pretrade_units'], n['posttrade_cash'], n['posttrade_units']) >= 0
        p, x, charged = n['price'], n['signed_nominal_USD'], n['fee_USD']
        near(p, points[i]['price'], 'input_price')
        near(n['volume'], points[i]['volume'], 'input_volume')
        near(n['fee_rate'], fee, 'fee_rate', True)
        near(n['pretrade_cash']+n['pretrade_units']*p, n['pretrade_equity'], 'pretrade_value')
        near(n['posttrade_cash']+n['posttrade_units']*p, n['posttrade_equity'], 'posttrade_value')
        near(n['posttrade_cash']-n['pretrade_cash'], -x-charged, 'cash_flow')
        near(n['posttrade_units']-n['pretrade_units'], x/p, 'units_flow')
        near(charged, abs(x)*fee, 'fee_once')
        near(n['pretrade_equity']-n['posttrade_equity'], charged, 'equity_fee')
        near(n['pretrade_exposure'], n['pretrade_units']*p/n['pretrade_equity'], 'pre_exposure', True)
        near(n['posttrade_exposure'], n['posttrade_units']*p/n['posttrade_equity'], 'post_exposure', True)
        if previous is not None:
            near(n['pretrade_cash'], previous['posttrade_cash'], 'cash_continuity')
            near(n['pretrade_units'], previous['posttrade_units'], 'units_continuity')
        if i == 0:
            near(n['pretrade_cash'], common['cash'], 'common_start_cash')
            near(n['pretrade_units'], common['units'], 'common_start_units')
            near(n['pretrade_equity'], 5000., 'common_start_value')
            if group == 'B':
                assert r['action'] == 'HOLD' and x == charged == 0
                assert r['target_if_action'] == ''
            else:
                assert r['action'] == 'ANNUAL_UPDATE'
                t = target['A_f2026'] if group == 'A' else cfg['fixed_k']
                near(float(r['target_if_action']), t, 'recorded_action_target', True)
                near(n['posttrade_exposure'], t, 'post_fee_target', True)
        elif i == 288:
            assert r['action'] == 'TERMINAL_LIQUIDATION' and float(r['target_if_action']) == 0
            assert n['posttrade_units'] == 0
            near(x, -n['pretrade_units']*p, 'terminal_full_sale')
        else:
            assert r['action'] == 'HOLD' and x == charged == 0 and r['target_if_action'] == ''
        if i < 288:
            nxt = rows[i+1]
            end = float(nxt['posttrade_equity'] if i == 287 else nxt['pretrade_equity'])
            rr = float(r['net_interval_return'])
            assert math.isfinite(rr) and rr > -1
            near(1+rr, end/n['pretrade_equity'], 'net_interval', True)
            returns.append(rr)
            exposures.append(n['posttrade_exposure'])
        else:
            assert r['net_interval_return'] == ''
        fees.append(charged)
        notionals.append(abs(x))
        marks.extend((n['pretrade_equity'], n['posttrade_equity']))
        previous = n
    terminal = float(rows[-1]['posttrade_cash'])
    near(5000*math.prod(1+x for x in returns), terminal, 'net_return_compound')
    vol = statistics.pstdev(returns)*math.sqrt(365)
    peak, dd = 5000., 0.
    for value in marks:
        peak = max(peak, value)
        dd = max(dd, (peak-value)/peak)
    market = float(rows[0]['posttrade_units'])*(points[-1]['price']-points[0]['price'])
    total_fees = math.fsum(fees)
    near(terminal, 5000+market-total_fees, 'wealth_contribution')
    m = {'terminal_cash_USD':terminal,'net_USD':terminal-5000,'annualized_population_volatility':vol,'maximum_drawdown':dd,'fees_USD':total_fees,'entry_fee_USD':fees[0],'exit_fee_USD':fees[-1],'reference_traded_notional_USD':math.fsum(notionals),'mean_holding_exposure':statistics.fmean(exposures),'post_update_units':float(rows[0]['posttrade_units']),'post_update_cash':float(rows[0]['posttrade_cash']),'inventory_mark_to_market_USD':market,'daily_intervals':288}
    m['Sharpe'] = statistics.fmean(returns)/statistics.pstdev(returns)*math.sqrt(365) if vol > 0 else None
    for field, value in m.items():
        if value is not None:
            near(value, result['all_six_accounts'][key][field], 'reported_'+field)
    assert len(returns) == 288
    assert result['all_six_accounts'][key]['trade_count'] == sum(x != 0 for x in notionals)
    metrics[key] = m

ratios, comparisons = {}, {}
risk_ok = True
for cost in ('50', '100'):
    a = metrics['A-'+cost]
    ratios[cost], comparisons[cost] = {}, {}
    for group in ('B', 'C'):
        z = metrics[group+'-'+cost]
        ratio = a['annualized_population_volatility']/z['annualized_population_volatility'] if z['annualized_population_volatility'] > 0 else None
        risk_ok = risk_ok and ratio is not None and math.isfinite(ratio) and .8 <= ratio <= 1.2
        ratios[cost][group] = ratio
        near(ratio, result['per_cost'][cost]['A_to_baseline_volatility_ratios'][group], 'reported_risk_ratio')
        difference = a['terminal_cash_USD']-z['terminal_cash_USD']
        market_difference = a['inventory_mark_to_market_USD']-z['inventory_mark_to_market_USD']
        fee_difference = a['fees_USD']-z['fees_USD']
        near(difference, market_difference-fee_difference, 'pairwise_contribution')
        comp = result['per_cost'][cost]['comparisons'][group]
        near(difference, comp['A_minus_baseline_USD'], 'reported_pairwise_cash')
        assert comp['A_strictly_leads'] == (difference > max(1e-6,1e-10*max(abs(a['terminal_cash_USD']),abs(z['terminal_cash_USD']),1)))
        assert comp['A_drawdown_not_worse'] == (a['maximum_drawdown'] <= z['maximum_drawdown']+1e-10)
        comparisons[cost][group] = {'A_minus_baseline_USD':difference,'market_difference_USD':market_difference,'fee_difference_USD':fee_difference}
assert risk_ok == result['risk_comparable_all_four_ratios']
assert not risk_ok and result['classification'] == 'INCONCLUSIVE_RISK_MISMATCH'

usage = resource.getrusage(resource.RUSAGE_SELF)
report = {
 'status':'PASS_ORIGINAL_ACCOUNTING_AND_FROZEN_CLASSIFICATION', 'must_fix':[],
 'verification_type':'read-only scalar/row/metric checks on original sealed six accounts; no strategy replay or new accounts; no adapter import or execution',
 'formal_market_runs_by_reviewer':0, 'original_csv_rows_checked':row_count, 'net_intervals_checked':row_count-6,
 'numerical_equalities_checked':checks, 'maximum_absolute_residuals_by_category':residuals,
 'original_result_classification':result['classification'], 'all_four_volatility_ratios':ratios,
 'verified_original_metrics':metrics, 'verified_pairwise_comparisons':comparisons,
 'source_to_sealed_points_exact_match':True, 'seed_and_common_start_verified':True,
 'local_recorded_seal_timeline_verified':timeline,
 'input_identities_actual':identities,
 'formal_resource_receipt':{'wall_seconds':receipt['whole_command_monotonic_wall_seconds'],'child_CPU_seconds':receipt['child_CPU_user_system_seconds'],'rusage_children_peak_RSS_bytes':receipt['rusage_children_peak_RSS_bytes_macOS'],'RSS_scope':'child/descendant maxima and sampled child; not continuous entire process tree'},
 'reviewer_command_resources':{'body_monotonic_wall_seconds':time.monotonic()-START,'process_CPU_user_system_seconds':usage.ru_utime+usage.ru_stime,'peak_RSS_bytes_macOS':usage.ru_maxrss,'CPU_limit_seconds':5},
 'limits':['Single inherited-inventory decision, conditional historical holdout, proxy Close fills and assumed costs only.','Risk qualification fails; do not relabel as comparable-risk superiority. All A results are below5000 and below B/C under both assumptions, but this is not universal failure of all risk methods.','Actual external personal costs/taxes, real execution/capacity and price-volume unit applicability are not verified here.','No live trade, account, network, model, new signal computation or market backtest was performed by reviewer.'],
 'actual_model':'UNKNOWN','actual_effort':'UNKNOWN','actual_route':'UNKNOWN','reviewer_UTC':datetime.now(timezone.utc).isoformat()
}
report['verifier_source'] = {'path':str(Path(__file__)), 'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
output = OUT/'original-accounting-verification.json'
with output.open('x') as f:
    json.dump(report, f, indent=2, ensure_ascii=False, allow_nan=False)
    f.write('\n')
print(json.dumps({'status':report['status'],'must_fix':[],'original_rows':row_count,'equalities':checks,'verification_report':str(output),'resources':report['reviewer_command_resources']},ensure_ascii=False))
