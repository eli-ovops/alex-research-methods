"""Read sealed ledgers only. No adapter imports, policy rerun, or new candidate account."""
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
import csv, hashlib, json, math, resource, statistics, sys, time

D = Path(__file__).resolve().parent.parent
R = D / 'review'
A = D / 'artifacts'
OLD = D.parent / 'annual-restart2020-execution-20261018'
K = 0.7853985165876642
START = time.perf_counter()
checks = 0
max_residual = 0.0

def read(p):
    return json.loads(Path(p).read_text())

def fingerprint(p):
    p = Path(p)
    return {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}

def check(condition, label):
    global checks
    checks += 1
    assert condition, label

def close(actual, expected, label, usd=False):
    global max_residual
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        check(actual == expected, label)
        return
    check(math.isfinite(actual) and math.isfinite(expected), label + ':finite')
    residual = abs(actual - expected)
    if usd:
        max_residual = max(max_residual, residual)
    tolerance = max(1e-8 if usd else 1e-12, 1e-10 * max(abs(actual), abs(expected)))
    check(residual <= tolerance, label + ':numeric')

def load(path):
    with Path(path).open(newline='') as f:
        records = list(csv.DictReader(f))
    for r in records:
        for k, v in list(r.items()):
            if v in ('True', 'False'):
                r[k] = v == 'True'
            elif v == '':
                r[k] = None
            elif k not in ('date', 'decision_UTC', 'feature_cutoff', 'method', 'generation_date'):
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
    return records

def audit_c(rows, refs, bps):
    check(len(rows) == len(refs) == 2192, 'C rows')
    pending = entered = False
    generation = None
    for i, (r, ref) in enumerate(zip(rows, refs)):
        day = date(2020, 1, 1) + timedelta(days=i)
        check(r['date'] == ref['date'] == str(day), 'date')
        check(r['decision_UTC'] == ref['decision_UTC'] == str(day) + 'T00:10:00Z', 'clock')
        check(r['feature_cutoff'] == ref['feature_cutoff'] == str(day-timedelta(days=2)), 'cutoff')
        check(r['method'] == 'C' and r['cost_bps'] == bps, 'C/cost')
        close(r['P'], float(ref['P']), 'price')
        close(r['reference_volume'], float(ref['reference_volume']), 'volume')
        check(r['P'] > 0 and r['reference_volume'] >= 0, 'valid references')
        terminal = i == len(rows)-1
        replaced = False
        if not terminal and (i == 0 or day.month == day.day == 1):
            replaced = pending
            pending = True
            generation = str(day.year) + '-01-01'
        attempt = terminal or pending
        target = 0.0 if terminal else K if attempt else None
        completed = attempt and r['reference_volume'] > 0
        check(r['terminal'] == terminal and r['attempt'] == attempt, 'attempt/terminal')
        check(r['pending_before'] == pending, 'pending before')
        check(r['newyear_replaced_pending'] == replaced, 'replacement')
        close(r['target_if_attempt'], target, 'target')
        close(r['frozen_target'], K, 'constant k')
        check(r['generation_date'] == generation, 'generation')
        check(r['allocation_completed'] == completed, 'completion')
        check(r['zero_volume_no_fill'] == (attempt and r['reference_volume'] == 0), 'no fill')
        if completed:
            pending = False
            if not terminal:
                entered = True
        check(r['pending_after'] == pending and r['entered_after_row'] == entered, 'pending after')
        prior_cash, prior_units = (5000.0, 0.0) if i == 0 else (rows[i-1]['posttrade_cash'], rows[i-1]['posttrade_units'])
        close(r['pretrade_cash'], prior_cash, 'cash continuity', True)
        close(r['pretrade_units'], prior_units, 'units continuity')
        p = r['P']
        pre = r['pretrade_cash'] + r['pretrade_units'] * p
        post = r['posttrade_cash'] + r['posttrade_units'] * p
        delta = r['posttrade_units'] - r['pretrade_units']
        fee = abs(delta) * p * bps / 10000
        check(pre > 0 and post > 0, 'positive wealth')
        close(r['pretrade_equity'], pre, 'pre equity', True)
        close(r['posttrade_equity'], post, 'post equity', True)
        close(r['trade_BTC'], delta, 'BTC change')
        close(r['reference_trade_USD'], abs(delta)*p, 'notional', True)
        close(r['cost_USD'], fee, 'fee', True)
        close(pre-post, fee, 'equity self finance', True)
        close(r['posttrade_cash'], r['pretrade_cash']-delta*p-fee, 'cash self finance', True)
        close(r['driftedweight'], r['pretrade_units']*p/pre, 'drifted weight')
        close(r['actualweight'], r['posttrade_units']*p/post, 'actual weight')
        check(r['posttrade_cash'] >= -1e-9 and r['posttrade_units'] >= -1e-9, 'no borrowing/short')
        if completed:
            close(r['actualweight'], target, 'completed target')
        else:
            check(r['posttrade_cash'] == r['pretrade_cash'] and r['posttrade_units'] == r['pretrade_units'] and r['cost_USD'] == 0, 'exact carry/no fee')
        if terminal:
            check(r['posttrade_units'] == 0 and r['net_interval_return'] is None, 'terminal cash')
        else:
            end = rows[i+1]['posttrade_equity'] if i == len(rows)-2 else rows[i+1]['pretrade_equity']
            close(r['net_interval_return'], end/r['pretrade_equity']-1, 'q includes fee once')
    close(5000*math.prod(1+r['net_interval_return'] for r in rows[:-1]), rows[-1]['posttrade_cash'], 'all returns wealth', True)

def describe(rows, indices):
    first, last = indices[0], indices[-1]
    final = last == len(rows)-2
    hold = [rows[i] for i in indices]
    transactions = hold + ([rows[-1]] if final else [])
    initial = rows[first]['pretrade_equity']
    ending = rows[-1]['posttrade_equity'] if final else rows[last+1]['pretrade_equity']
    q = [r['net_interval_return'] for r in hold]
    mean = math.fsum(q)/len(q)
    sd = math.sqrt(math.fsum((x-mean)**2 for x in q)/len(q))
    high = initial
    dd = 0.0
    for r in transactions:
        for v in (r['pretrade_equity'], r['posttrade_equity']):
            high = max(high, v)
            dd = max(dd, (high-v)/high)
    high = max(high, ending)
    dd = max(dd, (high-ending)/high)
    lastrow = rows[-1] if final else rows[last]
    return dict(start_equity_USD=initial, end_equity_USD=ending, net_USD=ending-initial,
        total_return=ending/initial-1, CAGR=(ending/initial)**(365/len(q))-1,
        annualized_volatility=sd*math.sqrt(365), Sharpe=mean/sd*math.sqrt(365) if sd else None,
        maximum_drawdown=dd, all_cost_USD=math.fsum(r['cost_USD'] for r in transactions),
        turnover=math.fsum(r['reference_trade_USD']/r['pretrade_equity'] for r in transactions),
        average_exposure=math.fsum(r['actualweight'] for r in hold)/len(hold),
        min_exposure=min(r['actualweight'] for r in hold), max_exposure=max(r['actualweight'] for r in hold),
        nonzero_trade_count=sum(r['trade_BTC'] != 0 for r in transactions),
        zero_volume_no_fill_count=sum(r['zero_volume_no_fill'] for r in transactions),
        zero_reference_volume_rows=sum(r['reference_volume'] == 0 for r in transactions),
        start_BTC=rows[first]['pretrade_units'], start_cash=rows[first]['pretrade_cash'],
        end_BTC=lastrow['posttrade_units'], end_cash=lastrow['posttrade_cash'],
        first_holding_date=rows[first]['date'], last_holding_date=rows[last]['date'],
        end_valuation_date=rows[last+1]['date'], intervals=len(q), terminal_fee_included=final)

def audit_metrics(rows, expected, label):
    overall = describe(rows, list(range(len(rows)-1)))
    for k, v in overall.items():
        close(expected['overall'][k], v, label + ':overall:' + k)
    check(expected['terminal_liquidated'] is True and expected['residual_BTC'] == 0, label+':liquidated')
    check(set(expected['all_six_years']) == set(map(str, range(2020, 2026))), label+':all years')
    for year in map(str, range(2020, 2026)):
        ix = [i for i, r in enumerate(rows[:-1]) if r['date'].startswith(year)]
        actual = describe(rows, ix)
        for k, v in actual.items():
            close(expected['all_six_years'][year][k], v, label+':'+year+':'+k)
    return overall

def main():
    protocol = read(D/'root/protocol.json')
    pre = read(A/'preflight-v2.json')
    result = read(A/'evaluation-results.json')
    seal = read(A/'final-result.seal.json')
    sixseal = read(A/'all-six-accounts-before-scoring.seal.json')
    config = read(A/'configuration-before-C.seal.json')
    gate_path = Path(next(iter(config['gate'])))
    gate = read(gate_path)
    for p, identity in pre['inputs'].items():
        check(fingerprint(p) == identity, 'original identity:'+p)
    for group in ('prepared_reference', 'adapter', 'protocol', 'supervisor'):
        for p, identity in pre[group].items():
            check(fingerprint(p) == identity, 'prepared identity:'+p)
    for group in ('existing_AB', 'new_C'):
        for p, identity in sixseal[group].items():
            check(fingerprint(p) == identity, 'six-ledger seal:'+p)
    for p, identity in seal['result'].items():
        check(fingerprint(p) == identity, 'result seal:'+p)
    check(fingerprint(A/'all-six-accounts-before-scoring.seal.json') == seal['ledger_seal'], 'ledger seal identity')
    check(fingerprint(A/'configuration-before-C.seal.json') == seal['configuration_seal'], 'configuration identity')
    check(fingerprint(A/'preflight-v2.json') == config['preflight'], 'configuration preflight identity')
    check(fingerprint(D/'execution/adapter.py') == config['adapter'], 'configuration adapter identity')
    check(fingerprint(D/'execution/formal-C-started.lock') == seal['lock'], 'one lock')
    check(seal['formal_units'] == 1 and seal['new_C_paths'] == 2, 'one formal unit/two C')
    check(config['UTC'] < sixseal['UTC'] < result['UTC'] < seal['UTC'], 'seal-before-score order')
    for p, identity in config['protocol'].items():
        check(fingerprint(p) == identity, 'protocol identity')
    for p, identity in config['gate'].items():
        check(fingerprint(p) == identity, 'gate identity')
    with (A/'reference-whitelist.csv').open(newline='') as f:
        refs = list(csv.DictReader(f))
    allmetrics = {}
    for bps in (25, 50):
        cost = str(bps)
        accounts = {m: load(A/f'C-fixedmix2020-{bps}bps-ledger.csv' if m=='C' else OLD/f'artifacts/{m}-fresh2020-{bps}bps-ledger.csv') for m in ('A','B','C')}
        audit_c(accounts['C'], refs, bps)
        for m in ('A', 'B'):
            for key in ('pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','cost_USD'):
                close(accounts['C'][0][key], accounts[m][0][key], 'common first:'+m+key)
            for cr, old in zip(accounts['C'], accounts[m]):
                if cr['date'] >= '2021-01-01':
                    close(cr['pretrade_equity'], old['pretrade_equity'], 'common 2021 Jan1 pretrade')
                    break
                for key in ('pretrade_cash','pretrade_units','pretrade_equity','posttrade_cash','posttrade_units','posttrade_equity','cost_USD','net_interval_return'):
                    close(cr[key], old[key], 'common 2020:'+m+key)
        allmetrics[cost] = {m: audit_metrics(rows, result['metrics'][cost][m], cost+m) for m, rows in accounts.items()}
    logs = {cost: math.log(m['A']['end_equity_USD']/m['C']['end_equity_USD']) for cost, m in allmetrics.items()}
    close(result['primary_25bps_log_WA_over_WC'], logs['25'], 'primary log')
    close(result['stress_50bps_log_WA_over_WC'], logs['50'], 'stress log')
    comparison = {}
    for cost, m in allmetrics.items():
        wa, wc = m['A']['end_equity_USD'], m['C']['end_equity_USD']
        da, dc = m['A']['maximum_drawdown'], m['C']['maximum_drawdown']
        tol = max(1e-6, 1e-10*max(abs(wa),abs(wc),1))
        comparison[cost] = dict(tie=abs(wa-wc)<=tol and abs(da-dc)<=1e-10,
            a_wins=wa>wc+tol and da<=dc+1e-10,
            c_nondegrading=wc>=wa-tol and dc<=da+1e-10,
            c_strict=wc>wa+tol or dc<da-1e-10,
            wealth_A_minus_C=wa-wc, DD_A_minus_C=da-dc, wealth_tolerance=tol)
        expected_flags = dict(wealth_A_minus_C=wa-wc, DD_A_minus_C=da-dc,
            USD_tolerance=tol, DD_tolerance=1e-10,
            A_wealth_strictly_higher=wa-wc>tol, A_DD_not_worse=da-dc<=1e-10,
            C_wealth_not_lower=wa-wc<=tol, C_DD_not_worse=da-dc>=-1e-10,
            C_wealth_strictly_higher=wa-wc<-tol, C_DD_strictly_lower=da-dc>1e-10,
            wealth_tied=abs(wa-wc)<=tol, DD_tied=abs(da-dc)<=1e-10,
            Sharpe_A_minus_C=m['A']['Sharpe']-m['C']['Sharpe'],
            volatility_A_minus_C=m['A']['annualized_volatility']-m['C']['annualized_volatility'],
            exposure_A_minus_C=m['A']['average_exposure']-m['C']['average_exposure'])
        for key, value in expected_flags.items():
            close(result['per_cost_comparison_flags'][cost][key], value, 'comparison flag:'+cost+key)
    if all(v['tie'] for v in comparison.values()):
        status='TIE'
    elif all(v['a_wins'] for v in comparison.values()):
        status='A_DESCRIPTIVELY_DOMINATES_C'
    elif all(v['c_nondegrading'] for v in comparison.values()) and any(v['c_strict'] for v in comparison.values()):
        status='C_DESCRIPTIVELY_DOMINATES_A'
    else:
        status='MIXED'
    check(result['combined_descriptive_classification'] == status, 'frozen joint classification')
    check(result['old_AB_gate_unchanged'] is True and result['new_independent_market_samples'] == 0 and result['fresh_OOS'] is False, 'claim limits')
    check(result['actual_trades'] == result['paid_resources'] == 0, 'no trade/payments')
    failed = read(A/'formal-command-receipt.json')
    recovered = read(A/'admission-recovered-formal-command-receipt.json')
    check(failed['exit_code'] == 1 and failed['formal_claim_exists'] is False, 'preserved pre-market failure')
    check(recovered['exit_code'] == 0 and recovered['stop_reason'] is None and recovered['formal_claim_exists'] is True and recovered['no_live_worker'] is True, 'single successful C market unit')
    elapsed = time.perf_counter()-START
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform.startswith('linux') else 1)
    check(rss <= 536870912 and elapsed < 600, 'checker resource limits')
    check(datetime.now(timezone.utc) < datetime.fromisoformat(protocol['resources']['work_hard_deadline_UTC'].replace('Z', '+00:00')), 'work deadline')
    check(failed['wall_seconds'] + recovered['wall_seconds'] + elapsed <= 600, 'cumulative computation/check budget')
    receipt = dict(status='PASS_VALID_'+status, UTC=datetime.now(timezone.utc).isoformat(), checks=checks,
        ledger_rows=6*2192, independent_check_elapsed_seconds=elapsed, checker_max_RSS_bytes=rss,
        max_accounting_USD_residual=max_residual, frozen_classification=status, comparison=comparison,
        logs=logs, pre_market_failed_command_wall_seconds=failed['wall_seconds'], market_formal_command_wall_seconds=recovered['wall_seconds'], cumulative_including_checker_internal_seconds=failed['wall_seconds']+recovered['wall_seconds']+elapsed, all_original_inputs_unchanged=pre['inputs'], fingerprints={str(p): fingerprint(p) for p in [Path(__file__),D/'root/protocol.json',gate_path,A/'preflight-v2.json',D/'execution/adapter.py',A/'configuration-before-C.seal.json',A/'all-six-accounts-before-scoring.seal.json',A/'evaluation-results.json',A/'final-result.seal.json',A/'formal-command-receipt.json',A/'admission-recovered-formal-command-receipt.json']},
        policy_reruns=0, candidate_ledgers_generated=0, model_runs=0, actual_trades=0, route='UNKNOWN')
    with (R/'final-check.json').open('x') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')
    print(json.dumps({k:receipt[k] for k in ('status','checks','ledger_rows','independent_check_elapsed_seconds','checker_max_RSS_bytes','max_accounting_USD_residual')},ensure_ascii=False))

if __name__ == '__main__':
    main()
