"""Independent, offline, no-model implementation of the frozen annual comparison."""
from pathlib import Path
import argparse, csv, hashlib, json, math, os, sys
from datetime import date, datetime, timedelta, timezone
import numpy as np

E = Path(__file__).resolve().parent
B = E.parent.parent
A = E / 'artifacts'
A.mkdir(exist_ok=True)
AUTH = E / 'authorization-and-budget.json'
AUTH_SHA = 'e71934fde63023503722add7720937d1288ddf771556f1598b653c8312909463'
OLD = B / 'evidence/BTC-daily-fixed-execution-20261017/artifacts'
DAILY = OLD / 'daily-source-inputs.csv'
OLD_SEAL = OLD / 'prepared-seal.json'
MODELS = ('risk_scaled_buy_hold', 'annual_units_hold')

def utc():
    return datetime.now(timezone.utc).isoformat()

def fp(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return {'sha256': h.hexdigest(), 'bytes': Path(p).stat().st_size}

def save(name, obj):
    p = A / name
    with p.open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    return p

def read(p):
    return json.loads(Path(p).read_text())

def check_deadline():
    deadline = datetime.fromisoformat(read(AUTH)['total_unit_deadline_UTC'])
    assert datetime.now(timezone.utc) < deadline, 'UTC_DEADLINE'

def fixed():
    assert fp(AUTH)['sha256'] == AUTH_SHA, 'AUTH_IDENTITY'
    au = read(AUTH)
    assert au['authorization'] == 'EXPLICITLY_APPROVED_ONCE'
    for k in ('plan', 'protocol'):
        assert fp(au[k])['sha256'] == au[k + '_sha256'], k + '_IDENTITY'
    cfg = read(au['protocol'])
    check_deadline()
    return au, cfg

def health():
    assert sys.version_info[:3] == (3, 12, 14), sys.version
    assert np.__version__ == '2.2.6'
    keys = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')
    assert all(os.environ.get(k) == '2' for k in keys)
    assert os.environ.get('PYTHONDONTWRITEBYTECODE') == '1'
    assert np.isfinite(np.array([0., 1.])).all()
    return {'UTC': utc(), 'pid': os.getpid(), 'Python': sys.version,
            'numpy': np.__version__, 'thread_environment': {k: os.environ[k] for k in keys},
            'no_model_import_or_construction': True, 'bytecode_disabled': True}

def step(cash, units, price, target, volume, attempt, bps):
    """Self financing exact proportional-cost allocation, not target-difference fee."""
    pre = cash + units * price
    assert pre > 0 and price > 0 and volume >= 0
    a = units * price / pre
    executed = bool(attempt and volume > 0)
    newcash, newunits = cash, units
    if executed:
        assert 0 <= target <= 1
        sign = 0 if target == a else (1 if target > a else -1)
        c = bps / 10000
        phi = (1 + c * sign * a) / (1 + c * sign * target)
        post = pre * phi
        newunits, newcash = target * post / price, (1 - target) * post
    post = newcash + newunits * price
    trade = newunits - units
    cost = abs(trade) * price * bps / 10000
    tol = max(1e-8, 1e-10 * pre)
    assert abs(pre - post - cost) <= tol
    assert abs(newcash - (cash - trade * price - cost)) <= tol
    assert newcash >= -1e-9 and newunits >= -1e-9
    assert all(math.isfinite(x) for x in (pre, post, cost, newcash, newunits))
    return newcash, newunits, {'pretrade_equity': pre, 'posttrade_equity': post,
            'pretrade_cash': cash, 'pretrade_units': units, 'driftedweight': a,
            'posttrade_cash': newcash, 'posttrade_units': newunits,
            'actualweight': newunits * price / post,
            'trade_BTC': trade, 'reference_trade_USD': abs(trade) * price,
            'cost_USD': cost, 'allocation_completed': executed,
            'zero_volume_no_fill': bool(attempt and volume == 0)}

def ledger(points, model, bps):
    cash, units = 5000., 0.
    pending, frozen, generation = False, None, None
    rows = []
    for i, p in enumerate(points):
        if i % 64 == 0:
            check_deadline()
        terminal = i == len(points) - 1
        newyear = p['date'].endswith('-01-01')
        replaced = False
        if model == 'annual_units_hold' and newyear and not terminal:
            replaced = pending
            frozen, generation, pending = p['annual_fraction'], p['date'], True
        pending_before = pending
        if terminal:
            attempt, target = True, 0.
        elif model == 'risk_scaled_buy_hold':
            attempt, target = True, p['v']
        else:
            attempt, target = pending, frozen
        oldcash, oldunits = cash, units
        cash, units, detail = step(cash, units, p['price'], target,
                                   p['volume'], attempt, bps)
        if model == 'annual_units_hold' and detail['allocation_completed']:
            pending = False
        row = {'date': p['date'], 'decision_UTC': p['date'] + 'T00:10:00Z',
               'feature_cutoff': p['feature_cutoff'], 'P': p['price'],
               'reference_volume': p['volume'], 'v_e': p['v'],
               'annual_f_y': frozen if model == 'annual_units_hold' else None,
               'annual_generation_date': generation,
               'pending_before': bool(pending_before), 'pending_after': bool(pending),
               'newyear_replaced_pending': bool(replaced), 'attempt': bool(attempt),
               'target_if_attempt': target if attempt else None,
               'terminal': terminal, 'cost_bps': bps, **detail}
        if not attempt or p['volume'] == 0:
            assert cash == oldcash and units == oldunits
        rows.append(row)
    valid = units == 0
    # Each q starts before its own transaction. Fold terminal transaction once.
    q = np.array([rows[i+1]['pretrade_equity'] / rows[i]['pretrade_equity'] - 1
                  for i in range(len(rows)-1)], dtype=np.float64)
    if len(q):
        q[-1] = rows[-1]['posttrade_equity'] / rows[-2]['pretrade_equity'] - 1
    assert np.isfinite(q).all() and np.all(q > -1)
    assert abs(float(np.prod(1+q))*5000-rows[-1]['posttrade_equity']) <= max(1e-8, 1e-10*rows[-1]['posttrade_equity'])
    for i, row in enumerate(rows):
        row['net_interval_return'] = float(q[i]) if i < len(q) else None
    return rows, q, valid

def fixture_points(dates, prices, volumes, v):
    return [{'date': d, 'price': p, 'volume': n, 'v': w, 'annual_fraction': w,
             'feature_cutoff': (date.fromisoformat(d)-timedelta(days=2)).isoformat()}
            for d,p,n,w in zip(dates, prices, volumes, v)]

def fixtures():
    # All numbers here are synthetic and are NOT market performance.
    p = fixture_points(['2020-01-01','2020-01-02','2020-01-03','2020-01-04'],
                       [100.,110.,120.,130.],[1.,1.,1.,1.],[.5,.2,.8,.3])
    rows,q,ok = ledger(p, 'annual_units_hold',25)
    assert ok and rows[0]['cost_USD']>0 and rows[-1]['cost_USD']>0
    assert rows[1]['cost_USD']==rows[2]['cost_USD']==0
    assert rows[0]['posttrade_units']==rows[1]['posttrade_units']==rows[2]['posttrade_units']
    assert rows[1]['actualweight']!=.5
    assert abs(sum(r['cost_USD'] for r in rows)-(rows[0]['cost_USD']+rows[-1]['cost_USD']))<1e-10
    p = fixture_points(['2020-01-01','2020-01-02','2020-01-03','2020-12-31',
                       '2021-01-01','2021-01-02','2021-01-03'],
                      [100.]*7,[0.,0.,1.,1.,0.,1.,1.],[.5,.1,.2,.3,.7,.1,.9])
    rows,_,ok = ledger(p,'annual_units_hold',25)
    assert ok and rows[2]['target_if_attempt']==.5 and rows[2]['allocation_completed']
    assert rows[3]['posttrade_units']==rows[2]['posttrade_units']
    assert rows[4]['pretrade_units']==rows[3]['posttrade_units']
    assert rows[5]['target_if_attempt']==.7 and rows[5]['allocation_completed']
    assert rows[-1]['target_if_attempt']==0 and rows[-1]['posttrade_units']==0
    p = fixture_points(['2020-01-01','2020-12-31','2021-01-01','2021-01-02','2021-01-03'],
                      [100.]*5,[0.,0.,0.,1.,0.],[.2,.2,.6,.8,.2])
    rows,_,ok = ledger(p,'annual_units_hold',25)
    assert rows[2]['newyear_replaced_pending'] and rows[3]['target_if_attempt']==.6
    assert not ok and rows[-1]['posttrade_units']>0
    p = fixture_points(['2020-12-31','2021-01-01'],[100.,100.],[1.,1.],[.5,.9])
    rows,_,ok = ledger(p,'annual_units_hold',25)
    assert ok and rows[-1]['target_if_attempt']==0 and rows[-1]['trade_BTC']==0
    assert summary_stats(np.zeros(3),[5000.]*4,5000.,5000.,[],[],True)['Sharpe']==0
    assert summary_stats(np.zeros(3),[5000.]*4,5000.,5000.,[],[],False)['Sharpe'] is None
    return {'status':'PASS_SYNTHETIC_ONLY','checks':['drift_units_carry','first_terminal_cost_once',
            'multiple_pending_days_freeze_f','crossyear_inheritance','newyear_replaces_pending',
            'terminal_priority','terminal_unfilled_invalid','zero_sd_only_cash_Sharpe0'],
            'market_results_computed':False}

def prepare():
    au,cfg = fixed()
    h = health()
    synth = fixtures()
    raw = cfg['data_reference_not_rescanned']
    assert fp(raw['path']) == {'sha256':raw['sha256'],'bytes':raw['bytes']}, 'CSV_HASH'
    seal = read(OLD_SEAL)
    assert fp(DAILY)==seal['inputs'][str(DAILY)], 'DAILY_HASH'
    allrows = list(csv.DictReader(DAILY.open()))
    complete = [r for r in allrows if r['complete']=='True']
    assert len(complete)==5402
    dates = [date.fromisoformat(r['date']) for r in complete]
    assert all(dates[i+1]-dates[i]==timedelta(days=1) for i in range(len(dates)-1))
    assert all(int(r['count'])==1440 and int(r['first_minute'])==0 and int(r['last_minute'])==1439 for r in complete)
    closes = np.array([float(r['close']) for r in complete],dtype=np.float64)
    prices = np.array([float(r['price']) for r in complete],dtype=np.float64)
    volumes = np.array([float(r['volume']) for r in complete],dtype=np.float64)
    assert np.isfinite(closes).all() and np.all(closes>0)
    assert np.isfinite(prices).all() and np.all(prices>0)
    assert np.isfinite(volumes).all() and np.all(volumes>=0)
    r = np.full(len(closes),np.nan);r[1:]=closes[1:]/closes[:-1]-1
    index = {d:i for i,d in enumerate(dates)}
    start,end = date(2014,1,1),date(2025,12,31)
    out=[];day=start;fy=None
    while day<=end:
        j=index[day];D=j-2
        sample=r[D-59:D+1]
        assert len(sample)==60 and np.isfinite(sample).all()
        assert dates[D]==day-timedelta(days=2)
        sigma=max(float(np.std(sample,ddof=0)),1e-6)
        v=min(1.,.4/(math.sqrt(365)*sigma))
        if day.month==1 and day.day==1:fy=v
        assert fy is not None
        out.append({'date':day.isoformat(),'price':float(prices[j]),'volume':float(volumes[j]),
                    'v':v,'annual_fraction':fy,'feature_cutoff':dates[D].isoformat()})
        day+=timedelta(days=1)
    p=A/'prepared-intents.csv'
    with p.open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    inputs={str(p):fp(p) for p in (AUTH,Path(au['plan']),Path(au['protocol']),Path(raw['path']),OLD_SEAL,DAILY)}
    sources={str(p):fp(p) for p in (E/'adapter.py',E/'supervise.py')}
    save('health.json',h);save('synthetic-fixtures.json',synth)
    save('preflight.json',{'UTC':utc(),'status':'STOPPED_BEFORE_MARKET_LEDGER_AND_METRICS',
        'inputs':inputs,'source_inputs':sources,'prepared':{str(p):fp(p)},
        'complete_days':len(complete),'scheduled_points':len(out),'holding_intervals':len(out)-1,
        'first':out[0]['date'],'terminal':out[-1]['date'],
        'annual_generations':[o['date'] for o in out if o['date'].endswith('-01-01')],
        'clock':'60 past returns through e-2, exact populationstd; no performance computed',
        'new_market_ledger_metrics_bootstrap':False,'model_import_fit_predict':False})
    print(json.dumps({'status':'STOPPED_BEFORE_MARKET_RUN','UTC':utc(),'points':len(out),'PID':os.getpid()}),flush=True)

def summary_stats(q,path,start,end,trades,holds,is_cash=False):
    sd=float(np.std(q,ddof=0));mean=float(np.mean(q));peak=path[0];dd=0.
    for v in path:
        peak=max(peak,v);dd=max(dd,1-v/peak)
    return {'start_equity_USD':start,'end_equity_USD':end,'net_USD':end-start,
            'total_return':end/start-1,'CAGR':(end/start)**(365/len(q))-1,
            'annualized_volatility':sd*math.sqrt(365),
            'Sharpe':math.sqrt(365)*mean/sd if sd>0 else (0. if is_cash and np.all(q==0) else None),
            'maximum_drawdown':dd,'cost_USD':sum(r['cost_USD'] for r in trades),
            'turnover':sum(r['reference_trade_USD']/r['pretrade_equity'] for r in trades),
            'average_exposure':sum(r['actualweight'] for r in holds)/len(holds),
            'min_exposure':min(r['actualweight'] for r in holds),
            'max_exposure':max(r['actualweight'] for r in holds),
            'zero_volume_no_fills':sum(r['zero_volume_no_fill'] for r in trades),
            'intervals':len(q)}

def metrics(rows,q,valid):
    path=[5000.]
    for r in rows:path.extend([r['pretrade_equity'],r['posttrade_equity']])
    overall=summary_stats(q,path,5000.,rows[-1]['posttrade_equity'],rows,rows[:-1])
    years={}
    for y in sorted({r['date'][:4] for r in rows[:-1]}):
        inds=[i for i,r in enumerate(rows[:-1]) if r['date'][:4]==y]
        first,last=inds[0],inds[-1];terminal=last==len(q)-1
        start=rows[first]['pretrade_equity']
        end=rows[-1]['posttrade_equity'] if terminal else rows[last+1]['pretrade_equity']
        trades=rows[first:last+1]+([rows[-1]] if terminal else [])
        yp=[start]
        for r in trades:yp.extend([r['pretrade_equity'],r['posttrade_equity']])
        yp.append(end)
        st=summary_stats(q[first:last+1],yp,start,end,trades,rows[first:last+1])
        # At Jan1's pretrade valuation, next-year trading has NOT occurred yet.
        endr=rows[-1] if terminal else rows[last]
        st.update({'start_BTC':rows[first]['pretrade_units'],'start_cash':rows[first]['pretrade_cash'],
                   'end_BTC':endr['posttrade_units'],'end_cash':endr['posttrade_cash'],
                   'first_interval':rows[first]['date'],'last_interval':rows[last]['date'],
                   'terminal_fee_included':terminal,'not_independent_yearly_test':True})
        assert abs(float(np.prod(1+q[first:last+1]))*start-end)<=max(1e-8,1e-10*end)
        years[y]=st
    return {'overall':overall,'every_year':years,'terminal_liquidated':valid,
            'residual_BTC':rows[-1]['posttrade_units']}

def bootstrap(d):
    rng=np.random.default_rng(20261017);n=len(d);offset=np.arange(90)
    samples=np.empty(10000,dtype=np.float64)
    for i in range(10000):
        if i%100==0:check_deadline()
        starts=rng.integers(0,n,size=math.ceil(n/90))
        ix=((starts[:,None]+offset)%n).ravel()[:n]
        samples[i]=np.mean(d[ix])
    return {'paired_mean_log_excess':float(np.mean(d)),
            'one_sided95_lower':float(np.quantile(samples,.05,method='linear')),
            'block_days':90,'replicates':10000,'seed':20261017,
            'quantile_method':'linear','historical_selection_bias_not_removed':True}

def run(approval):
    au,cfg=fixed();health()
    gate=read(approval)
    assert gate.get('allow_market_run') is True, 'GATE_NOT_ALLOWED'
    pre=read(A/'preflight.json')
    for collection in ('inputs','source_inputs','prepared'):
        for path,identity in pre[collection].items():assert fp(path)==identity,'PREFLIGHT_IDENTITY:'+path
    for path,identity in gate['source_inputs'].items():assert fp(path)==identity,'GATE_SOURCE:'+path
    assert set(gate['source_inputs'])==set(pre['source_inputs'])
    claim=E/'market-run-started.lock'
    with claim.open('x') as f:json.dump({'UTC':utc(),'PID':os.getpid(),'approval':str(approval),'gate_identity':fp(approval)},f)
    points=[]
    for r in csv.DictReader((A/'prepared-intents.csv').open()):
        points.append({k:(float(v) if k in ('price','volume','v','annual_fraction') else v) for k,v in r.items()})
    save('intentions-before-ledgers.seal.json',{'UTC':utc(),'inputs':pre['inputs'],
         'intentions':pre['prepared'],'sources':pre['source_inputs'],'approval':fp(approval),
         'no_new_model':True})
    allruns={};ledger_files=[]
    for model in MODELS:
        for bps in (25,50):
            rows,q,valid=ledger(points,model,bps)
            p=A/(model+'-'+str(bps)+'bps-ledger.csv')
            with p.open('x',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            ledger_files.append(p);allruns[(model,bps)]=(rows,q,valid)
    save('all-four-ledgers-before-summary.seal.json',{'UTC':utc(),
         'ledger_inputs':{str(p):fp(p) for p in ledger_files},'scoring_not_started':True})
    stats={model:{str(bps):metrics(*allruns[(model,bps)]) for bps in (25,50)} for model in MODELS}
    candidate,control=MODELS
    ratios={};risk_ok=True
    for bps in (25,50):
        a=stats[candidate][str(bps)]['overall']['annualized_volatility'];b=stats[control][str(bps)]['overall']['annualized_volatility']
        ratio=a/b if b>0 else None;ratios[str(bps)]=ratio
        risk_ok &= ratio is not None and .8<=ratio<=1.2
    d=np.log1p(allruns[(candidate,25)][1])-np.log1p(allruns[(control,25)][1])
    bt=bootstrap(d)
    a,b=stats[candidate]['25']['overall'],stats[control]['25']['overall']
    sa,sb=stats[candidate]['50']['overall'],stats[control]['50']['overall']
    stress_d=np.log1p(allruns[(candidate,50)][1])-np.log1p(allruns[(control,50)][1])
    gates={'risk_qualified_both_costs':bool(risk_ok),'net_positive_primary':a['net_USD']>0,
        'Sharpe_increment_ge_020':a['Sharpe'] is not None and b['Sharpe'] is not None and a['Sharpe']-b['Sharpe']>=.2,
        'DD_not_larger_primary':a['maximum_drawdown']<=b['maximum_drawdown'],
        'paired_mean_positive':bt['paired_mean_log_excess']>0,'paired_lower_positive':bt['one_sided95_lower']>0,
        'stress_net_positive':sa['net_USD']>0,'stress_paired_mean_positive':bool(np.mean(stress_d)>0),
        'stress_Sharpe_not_lower':sa['Sharpe'] is not None and sb['Sharpe'] is not None and sa['Sharpe']>=sb['Sharpe'],
        'stress_DD_not_larger':sa['maximum_drawdown']<=sb['maximum_drawdown'],
        'all_terminal_liquidated':all(x[2] for x in allruns.values())}
    status=('TECHNICALLY_INVALID' if not gates['all_terminal_liquidated'] else
            'INCONCLUSIVE_RISK_MISMATCH' if not risk_ok else
            'HISTORICAL_CANDIDATE_SUPPORTED_ONLY' if all(gates.values()) else 'NOT_SUPPORTED_THIS_DIAGNOSTIC')
    p=save('evaluation-results.json',{'UTC':utc(),'status':status,'metrics':stats,
        'risk_ratios':ratios,'primary_paired_test':bt,'stress_paired_mean':float(np.mean(stress_d)),
        'gates':gates,'all_years_retained':True,'fresh_OOS':False,'real_trades':False,
        'wealth_goal_achieved':False,'no_risk_rescaling_or_parameter_change':True})
    save('final-result.seal.json',{'UTC':utc(),'result':{str(p):fp(p)},
         'unchanged_inputs':{path:fp(path) for path in pre['inputs']},'single_market_claim':fp(claim)})
    print(json.dumps({'UTC':utc(),'status':status,'single_market_run':True}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','run']);parser.add_argument('--approval')
    args=parser.parse_args()
    if args.stage=='prepare':prepare()
    else:
        assert args.approval
        run(Path(args.approval))
