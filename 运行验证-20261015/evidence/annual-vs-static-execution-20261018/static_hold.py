"""Independent standard-library B accounting; never imports or reruns A strategy."""
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
import argparse, csv, hashlib, json, math, os, statistics, sys

D=Path(__file__).resolve().parent
A=D/'artifacts'
A.mkdir(exist_ok=True)
AUTH=D/'root-admission.json'
AUTH_SHA='2d131b831f7eca74a661d64d4f6cd5ddad448b6c2621e31e8fd98890527668e7'
OLD=D.parent/'risk-scaled-vs-annual-execution-20261017'
RESULT=OLD/'artifacts/evaluation-results.json'
RESULT_SHA='fda532a2c8e91bddc8a374444b841ffbb5191dcfc5c5046c669b94dd1df51b1c'
REVIEW=OLD/'review-final/review.json'
REVIEW_SHA='5e60040e33bf860cceafff39656366e458fe10796c2954c9bba57e22b854f249'
NUMERIC=('P','reference_volume','annual_f_y','pretrade_equity','posttrade_equity',
    'pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','actualweight',
    'trade_BTC','reference_trade_USD','cost_USD')

def utc():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def fp(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return {'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def save(name,obj):
    p=A/name
    with p.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    return p
def check_deadline():
    assert datetime.now(timezone.utc)<datetime.fromisoformat(read(AUTH)['total_work_deadline_utc']),'UTC_DEADLINE'
def load_fixed():
    assert fp(AUTH)['sha256']==AUTH_SHA,'AUTH_IDENTITY'
    au=read(AUTH)
    for key in ('plan','static_protocol'):
        assert fp(au[key]['path'])['sha256']==au[key]['sha256'],key+'_IDENTITY'
    cfg=read(au['static_protocol']['path'])
    check_deadline()
    return au,cfg
def health():
    assert sys.version_info[:3]==(3,12,14),sys.version
    keys=('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS',
          'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')
    assert all(os.environ.get(k)=='2' for k in keys)
    assert os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    return {'UTC':utc(),'PID':os.getpid(),'Python':sys.version,'stdlib_only':True,
            'threads':{k:os.environ[k] for k in keys},'no_scientific_or_model_imports':True,
            'single_accounting_worker_no_threadpool':True}

def load_A(path):
    with Path(path).open(newline='') as f:
        records=list(csv.DictReader(f))
    rows=[]
    for r in records:
        x={k:float(r[k]) for k in NUMERIC}
        x.update(date=r['date'],decision_UTC=r['decision_UTC'],feature_cutoff=r['feature_cutoff'],
                 terminal=r['terminal']=='True',net_interval_return=float(r['net_interval_return']) if r['net_interval_return'] else None,
                 zero_volume_no_fill=r['zero_volume_no_fill']=='True',
                 allocation_completed=r['allocation_completed']=='True')
        rows.append(x)
    return rows

def inspect_A(rows,bps):
    assert len(rows)==4383 and rows[0]['date']=='2014-01-01' and rows[-1]['date']=='2025-12-31'
    assert rows[0]['pretrade_cash']==5000 and rows[0]['pretrade_units']==0
    assert rows[0]['allocation_completed'] and rows[0]['reference_volume']>0
    assert rows[-1]['terminal'] and rows[-1]['net_interval_return'] is None
    for i,r in enumerate(rows):
        assert all(math.isfinite(r[k]) for k in NUMERIC)
        day=date.fromisoformat(r['date'])
        assert r['decision_UTC']==r['date']+'T00:10:00Z'
        assert r['feature_cutoff']==(day-timedelta(days=2)).isoformat()
        assert r['P']>0 and r['reference_volume']>=0
        if i:assert day-date.fromisoformat(rows[i-1]['date'])==timedelta(days=1)
    return {'rows':len(rows),'first':rows[0]['decision_UTC'],'terminal':rows[-1]['decision_UTC'],
            'initial_source_units':rows[0]['posttrade_units'],'initial_source_cash':rows[0]['posttrade_cash'],
            'initial_fee':rows[0]['cost_USD'],'cost_bps':bps,'new_performance_computed':False}

def close_units(cash,units,price,volume,bps):
    if volume==0:return cash,units,0.,0.,False
    nominal=units*price;cost=nominal*bps/10000
    return cash+nominal-cost,0.,-units,cost,True

def build_B(source,bps):
    """One first-row copy, exact-unit/cash carry, one terminal close; no reweight."""
    rows=[];cash=5000.;units=0.
    for i,r in enumerate(source):
        terminal=i==len(source)-1;P=r['P'];pre=cash+units*P
        oldcash,oldunits=cash,units
        trade=cost=0.;attempt=False;completed=False
        if i==0:
            assert r['allocation_completed'] and r['pretrade_cash']==5000. and r['pretrade_units']==0.
            cash,units=r['posttrade_cash'],r['posttrade_units']
            trade,cost=r['trade_BTC'],r['cost_USD'];attempt=completed=True
        elif terminal:
            attempt=True
            cash,units,trade,cost,completed=close_units(cash,units,P,r['reference_volume'],bps)
        post=cash+units*P;tol=max(1e-8,1e-10*pre)
        assert abs(pre-post-cost)<=tol
        assert abs(cash-(oldcash-trade*P-cost))<=tol
        assert cash>=-1e-9 and units>=-1e-9
        if i not in (0,len(source)-1):assert units==oldunits and cash==oldcash
        x={'date':r['date'],'decision_UTC':r['decision_UTC'],'feature_cutoff':r['feature_cutoff'],
           'P':P,'reference_volume':r['reference_volume'],'initial_target':source[0]['annual_f_y'],
           'cost_bps':bps,'attempt':attempt,'allocation_completed':completed,'terminal':terminal,
           'pretrade_equity':pre,'posttrade_equity':post,'pretrade_units':oldunits,'pretrade_cash':oldcash,
           'posttrade_units':units,'posttrade_cash':cash,'actualweight':units*P/post,
           'trade_BTC':trade,'reference_trade_USD':abs(trade)*P,'cost_USD':cost,
           'zero_volume_no_fill':bool(attempt and r['reference_volume']==0),'net_interval_return':None}
        assert all(math.isfinite(x[k]) for k in ('P','pretrade_equity','posttrade_equity','cost_USD','actualweight'))
        rows.append(x)
    for i in range(len(rows)-1):
        rows[i]['net_interval_return']=rows[i+1]['pretrade_equity']/rows[i]['pretrade_equity']-1
    rows[-2]['net_interval_return']=rows[-1]['posttrade_equity']/rows[-2]['pretrade_equity']-1
    return rows

def stats(rows,first,last):
    """Holding intervals first..last inclusive, from a continuous sealed account."""
    terminal=last==len(rows)-2
    start=rows[first]['pretrade_equity']
    end=rows[-1]['posttrade_equity'] if terminal else rows[last+1]['pretrade_equity']
    q=[r['net_interval_return'] for r in rows[first:last+1]]
    assert all(math.isfinite(x) and x>-1 for x in q)
    sd=statistics.pstdev(q);mean=statistics.fmean(q)
    trades=rows[first:last+1]+([rows[-1]] if terminal else [])
    path=[start]
    for r in trades:path.extend((r['pretrade_equity'],r['posttrade_equity']))
    path.append(end);peak=path[0];dd=0.
    for v in path:peak=max(peak,v);dd=max(dd,1-v/peak)
    endrow=rows[-1] if terminal else rows[last]
    holds=rows[first:last+1]
    assert abs(start*math.prod(1+x for x in q)-end)<=max(1e-8,1e-10*end)
    return {'start_equity_USD':start,'end_equity_USD':end,'net_USD':end-start,
            'total_return':end/start-1,'CAGR':(end/start)**(365/len(q))-1,
            'annualized_volatility':sd*math.sqrt(365),'Sharpe':math.sqrt(365)*mean/sd if sd>0 else None,
            'maximum_drawdown':dd,'all_cost_USD':math.fsum(r['cost_USD'] for r in trades),
            'turnover':math.fsum(r['reference_trade_USD']/r['pretrade_equity'] for r in trades),
            'average_exposure':statistics.fmean(r['actualweight'] for r in holds),
            'min_exposure':min(r['actualweight'] for r in holds),'max_exposure':max(r['actualweight'] for r in holds),
            'nonzero_trade_count':sum(r['trade_BTC']!=0 for r in trades),
            'zero_volume_no_fill_count':sum(r['zero_volume_no_fill'] for r in trades),
            'zero_reference_volume_rows':sum(r['reference_volume']==0 for r in trades),
            'start_BTC':rows[first]['pretrade_units'],'start_cash':rows[first]['pretrade_cash'],
            'end_BTC':endrow['posttrade_units'],'end_cash':endrow['posttrade_cash'],
            'intervals':len(q),'first_holding_date':rows[first]['date'],'last_holding_date':rows[last]['date'],
            'end_valuation_date':rows[last+1]['date'],'terminal_fee_included':terminal,
            'log_growth':math.fsum(math.log1p(x) for x in q)}

def all_metrics(rows):
    n=len(rows)-2;years={}
    for year in sorted({r['date'][:4] for r in rows[:-1]}):
        ix=[i for i,r in enumerate(rows[:-1]) if r['date'][:4]==year]
        years[year]=stats(rows,ix[0],ix[-1])
    cut=next(i for i,r in enumerate(rows) if r['date']=='2020-01-01')
    return {'overall':stats(rows,0,n),'years':years,'fixed_halves':{
        '2014-2019':stats(rows,0,cut-1),'2020-2025':stats(rows,cut,n)},
        'terminal_liquidated':rows[-1]['posttrade_units']==0}

def synthetic():
    # No market inputs. A source-like initial transaction has exact c=.0025.
    p=100.;c=.0025;w=.5;post=5000/(1+c*w);u=w*post/p;cash=(1-w)*post
    dates=['2019-12-30','2019-12-31','2020-01-01','2020-01-02']
    source=[]
    for day,P in zip(dates,[100.,110.,120.,130.]):
        source.append({'date':day,'decision_UTC':day+'T00:10:00Z','feature_cutoff':'synthetic',
          'P':P,'reference_volume':1.,'annual_f_y':w,'allocation_completed':True,
          'pretrade_cash':5000.,'pretrade_units':0.,'posttrade_cash':cash,'posttrade_units':u,
          'trade_BTC':u,'cost_USD':c*u*p})
    rows=build_B(source,25)
    assert rows[1]['trade_BTC']==rows[2]['trade_BTC']==0
    assert rows[0]['posttrade_units']==rows[1]['posttrade_units']==rows[2]['posttrade_units']
    assert rows[0]['posttrade_cash']==rows[1]['posttrade_cash']==rows[2]['posttrade_cash']
    assert rows[0]['pretrade_equity']==5000 and rows[0]['cost_USD']==source[0]['cost_USD']
    assert rows[-1]['posttrade_units']==0 and rows[-1]['net_interval_return'] is None
    assert rows[-2]['net_interval_return']==rows[-1]['posttrade_equity']/rows[-2]['pretrade_equity']-1
    assert sum(r['cost_USD'] for r in rows)==rows[0]['cost_USD']+rows[-1]['cost_USD']
    y19=stats(rows,0,1);y20=stats(rows,2,2)
    assert y19['end_equity_USD']==rows[2]['pretrade_equity']==y20['start_equity_USD']
    assert not y19['terminal_fee_included'] and y20['terminal_fee_included']
    assert y19['end_BTC']==y20['start_BTC'] and y19['end_cash']==y20['start_cash']
    source[-1]['reference_volume']=0
    fail=build_B(source,25);assert fail[-1]['posttrade_units']>0 and fail[-1]['cost_USD']==0
    # Both pre and post are retained for drawdown; no redundant terminal charge.
    assert y19['maximum_drawdown']>=1-rows[0]['posttrade_equity']/5000
    return {'status':'PASS_NONMARKET_SYNTHETIC','fixtures':['first_fee_once_with5000_start',
        'exact_units_cash_carry_and_drift','ordinary_interval_cost_alignment','terminal_fee_once_terminal_q_empty',
        'year_and_2020_pretrade_boundary_inheritance','pre_post_drawdown_points','terminal_nofill_unliquidated'],
        'market_ledger_or_performance_created':False}

def prepare():
    au,cfg=load_fixed();h=health();fx=synthetic()
    inputs={str(AUTH):fp(AUTH),str(Path(au['plan']['path'])):fp(au['plan']['path']),
            str(Path(au['static_protocol']['path'])):fp(au['static_protocol']['path'])}
    checks={};anchors={}
    for cost in (25,50):
        ref=cfg['A']['ledgers'][str(cost)];assert fp(ref['path'])=={k:ref[k] for k in ('sha256','bytes')}
        inputs[ref['path']]=fp(ref['path']);rows=load_A(ref['path']);checks[str(cost)]=inspect_A(rows,cost)
        anchors[str(cost)]={k:rows[0][k] for k in ('date','decision_UTC','P','annual_f_y','pretrade_cash',
                            'pretrade_units','posttrade_cash','posttrade_units','cost_USD')}
    assert fp(RESULT)['sha256']==RESULT_SHA and fp(REVIEW)['sha256']==REVIEW_SHA
    inputs[str(RESULT)]=fp(RESULT);inputs[str(REVIEW)]=fp(REVIEW)
    save('health.json',h);save('synthetic-fixtures.json',fx)
    save('preflight.json',{'UTC':utc(),'status':'STOPPED_BEFORE_FORMAL_B_MARKET_PATH',
        'inputs':inputs,'source_inputs':{str(p):fp(p) for p in (D/'static_hold.py',D/'supervise.py')},
        'A_readonly_structure':checks,'B_initial_state_verbatim_A_anchors':anchors,
        'no_A_or_B_market_path_generated':True,'market_metrics_bootstrap_models':False,
        'git_markers':{str(p): (p/'.git').exists() for p in (D,D.parent,D.parent.parent,D.parent.parent.parent)}})
    print(json.dumps({'UTC':utc(),'PID':os.getpid(),'status':'STOPPED_BEFORE_FORMAL_B_MARKET_PATH'}),flush=True)

def run(gate_path):
    au,cfg=load_fixed();health();gate=read(gate_path);pre=read(A/'preflight.json')
    assert gate.get('allow_B_market_run') is True
    for group in ('inputs','source_inputs'):
        for p,ident in pre[group].items():assert fp(p)==ident,'PREFLIGHT_IDENTITY:'+p
    assert gate['source_inputs']==pre['source_inputs']
    for p,ident in gate.get('inputs',{}).items():assert fp(p)==ident,'GATE_INPUT:'+p
    with (D/'formal-B-run-started.lock').open('x') as f:
        json.dump({'UTC':utc(),'PID':os.getpid(),'gate':str(gate_path),'gate_identity':fp(gate_path)},f)
    save('configuration-before-B.seal.json',{'UTC':utc(),'inputs':pre['inputs'],
        'source_inputs':pre['source_inputs'],'configuration':fp(au['static_protocol']['path']),'gate':fp(gate_path)})
    accounts={};bs=[]
    for cost in (25,50):
        check_deadline();original=load_A(cfg['A']['ledgers'][str(cost)]['path']);B=build_B(original,cost)
        for k in ('pretrade_equity','posttrade_equity','pretrade_cash','pretrade_units','posttrade_cash',
                  'posttrade_units','cost_USD','trade_BTC'):assert B[0][k]==original[0][k]
        p=A/f'B-static-units-{cost}bps-ledger.csv'
        with p.open('x',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(B[0]));wr.writeheader();wr.writerows(B)
        accounts[str(cost)]={'A':original,'B':B};bs.append(p)
    save('both-B-ledgers-before-scoring.seal.json',{'UTC':utc(),'B_ledgers':{str(p):fp(p) for p in bs},
        'A_ledger_references':cfg['A']['ledgers'],'all_B_rows_sealed_before_scoring':True})
    output={};risk={};paired={};ratios_ok=True;valid=True
    old=read(RESULT)['metrics']['annual_units_hold']
    for cost,acct in accounts.items():
        check_deadline();output[cost]={k:all_metrics(rows) for k,rows in acct.items()}
        am,bm=output[cost]['A'],output[cost]['B'];valid &= am['terminal_liquidated'] and bm['terminal_liquidated']
        # Score already sealed A observations, never regenerate an A position path.
        for k in ('net_USD','CAGR','Sharpe','annualized_volatility','maximum_drawdown','turnover','average_exposure'):
            assert math.isclose(am['overall'][k],old[cost]['overall'][k],rel_tol=1e-9,abs_tol=1e-8),'SEALED_A_STATS:'+k
        va,vb=am['overall']['annualized_volatility'],bm['overall']['annualized_volatility']
        ratio=va/vb if vb>0 else None;risk[cost]=ratio;ratios_ok &= ratio is not None and .8<=ratio<=1.2
        diffs=[math.log1p(a['net_interval_return'])-math.log1p(b['net_interval_return']) for a,b in zip(acct['A'][:-1],acct['B'][:-1])]
        paired[cost]={'full_mean_daily_log_excess_A_minus_B':statistics.fmean(diffs),
          'every_year_log_growth_difference':{y:am['years'][y]['log_growth']-bm['years'][y]['log_growth'] for y in am['years']},
          'fixed_halves_A_growth_factor_over_B_growth_factor':{h:(1+am['fixed_halves'][h]['total_return'])/(1+bm['fixed_halves'][h]['total_return']) for h in am['fixed_halves']},
          'no_significance_tests':True}
    a,b=output['25']['A']['overall'],output['25']['B']['overall'];s,t=output['50']['A']['overall'],output['50']['B']['overall']
    sharpe_defined=all(x['Sharpe'] is not None for x in (a,b,s,t))
    gates={'risk_qualified_both_costs':bool(ratios_ok),'terminal_liquidation_valid':bool(valid),
       'A25_positive_and_wealth_greater_B':a['net_USD']>0 and a['end_equity_USD']>b['end_equity_USD'],
       'A25_Sharpe_ge_B_plus020':sharpe_defined and a['Sharpe']>=b['Sharpe']+.20,
       'A25_DD_not_larger':a['maximum_drawdown']<=b['maximum_drawdown'],
       'A50_positive_and_wealth_greater_B':s['net_USD']>0 and s['end_equity_USD']>t['end_equity_USD'],
       'A50_Sharpe_not_lower':sharpe_defined and s['Sharpe']>=t['Sharpe'],
       'A50_DD_not_larger':s['maximum_drawdown']<=t['maximum_drawdown']}
    status=('TECHNICALLY_INVALID' if not valid else 'INCONCLUSIVE_RISK_MISMATCH' if not ratios_ok else
            'DESCRIPTIVE_HISTORICAL_ADVANTAGE' if all(gates.values()) else 'NOT_SUPPORTED_THIS_DIAGNOSTIC')
    p=save('evaluation-results.json',{'UTC':utc(),'status':status,'metrics':output,'risk_ratios_A_over_B':risk,
        'paired_descriptions':paired,'gates':gates,'A_sealed_statistics_match':True,'A_strategy_rerun':False,
        'all_12_years_and_both_halves_reported':True,'no_new_model_or_tests':True,'fresh_OOS':False,
        'actual_execution_costs_capacity_and_PIT':'UNKNOWN','actual_trades':0,'wealth_goal_achieved':False})
    save('final-result.seal.json',{'UTC':utc(),'result':{str(p):fp(p)},
        'all_inputs_unchanged':{p:fp(p) for p in pre['inputs']},'formal_claim':fp(D/'formal-B-run-started.lock')})
    print(json.dumps({'UTC':utc(),'status':status,'formal_B_unit_count':1}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','run'));ap.add_argument('--approval');args=ap.parse_args()
    if args.stage=='prepare':prepare()
    else:
        assert args.approval
        run(Path(args.approval))
