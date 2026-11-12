"""Owned stdlib-only fresh-capital accounting; does not import any old adapter."""
from pathlib import Path
from datetime import date,datetime,timedelta,timezone
import argparse,csv,hashlib,json,math,os,statistics,sys

D=Path(__file__).resolve().parent
A=D/'artifacts';A.mkdir(exist_ok=True)
AUTH=D/'root-admission.json'
AUTH_SHA='e08982423318df32e9ca49f1a761cf048069dc758ff0d451cbb22db466275462'
SOURCE_KEYS=('date','decision_UTC','feature_cutoff','P','reference_volume','annual_f_y',
             'annual_generation_date','pending_before','pending_after','attempt',
             'allocation_completed','zero_volume_no_fill','terminal')

def utc():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def fp(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1048576),b''):h.update(x)
    return {'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def save(name,obj):
    p=A/name
    with p.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    return p
def deadline():
    assert datetime.now(timezone.utc)<datetime.fromisoformat(read(AUTH)['work_deadline_UTC']),'UTC_DEADLINE'
def fixed():
    assert fp(AUTH)['sha256']==AUTH_SHA,'AUTH_IDENTITY'
    au=read(AUTH);files=au['files'];inputs={str(AUTH):fp(AUTH)};cfg=None
    for name,ref in files.items():
        identity=fp(ref['path']);assert identity=={'sha256':ref['sha256'],'bytes':ref['bytes']},name
        inputs[ref['path']]=identity
        if name.endswith('protocol-draft.json'):cfg=read(ref['path'])
    assert cfg is not None and cfg['protocol_id']==au['protocol_id']
    deadline();return au,cfg,inputs
def health():
    assert sys.version_info[:3]==(3,12,14),sys.version
    keys=('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')
    assert all(os.environ.get(k)=='2' for k in keys)
    assert os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    return {'UTC':utc(),'PID':os.getpid(),'Python':sys.version,'stdlib_only':True,
            'thread_environment':{k:os.environ[k] for k in keys},
            'no_models_scientific_packages_or_old_adapter_imported':True}

def transaction(cash,units,price,volume,target,attempt,bps):
    pre=cash+units*price;oldcash,oldunits=cash,units
    assert pre>0 and price>0 and volume>=0
    a=units*price/pre;completed=bool(attempt and volume>0)
    if completed:
        assert target is not None and 0<=target<=1
        sign=0 if target==a else (1 if target>a else -1)
        c=bps/10000;phi=(1+c*sign*a)/(1+c*sign*target)
        post=pre*phi;units=target*post/price;cash=(1-target)*post
    post=cash+units*price;delta=units-oldunits;nominal=abs(delta)*price;fee=nominal*bps/10000
    tol=max(1e-8,1e-10*pre)
    assert abs(pre-post-fee)<=tol and abs(cash-(oldcash-delta*price-fee))<=tol
    assert cash>=-1e-9 and units>=-1e-9
    assert all(math.isfinite(x) for x in (pre,post,cash,units,delta,fee))
    if not completed:assert cash==oldcash and units==oldunits
    return cash,units,{'pretrade_equity':pre,'posttrade_equity':post,'pretrade_cash':oldcash,
        'pretrade_units':oldunits,'posttrade_cash':cash,'posttrade_units':units,
        'driftedweight':a,'actualweight':units*price/post,'trade_BTC':delta,
        'reference_trade_USD':nominal,'cost_USD':fee,'allocation_completed':completed,
        'zero_volume_no_fill':bool(attempt and volume==0)}

def ledger(points,method,bps):
    cash,units=5000.,0.;pending=False;entered=False;frozen=None;generation=None;rows=[]
    for i,p in enumerate(points):
        if i%128==0:deadline()
        terminal=i==len(points)-1;newyear=p['date'].endswith('-01-01');replaced=False
        if not terminal and (i==0 or (newyear and (method=='A' or not entered))):
            replaced=pending;frozen=p['annual_f_y'];generation=p['annual_generation_date'];pending=True
        before=pending
        attempt=True if terminal else pending
        target=0. if terminal else frozen if attempt else None
        cash,units,detail=transaction(cash,units,p['P'],p['reference_volume'],target,attempt,bps)
        if detail['allocation_completed']:
            pending=False
            if not terminal:entered=True
        rows.append({'date':p['date'],'decision_UTC':p['decision_UTC'],'feature_cutoff':p['feature_cutoff'],
          'P':p['P'],'reference_volume':p['reference_volume'],'method':method,'cost_bps':bps,
          'frozen_target':frozen,'generation_date':generation,'pending_before':before,'pending_after':pending,
          'newyear_replaced_pending':replaced,'attempt':attempt,'target_if_attempt':target,
          'entered_after_row':entered,'terminal':terminal,**detail,'net_interval_return':None})
    for i in range(len(rows)-1):
        rows[i]['net_interval_return']=rows[i+1]['pretrade_equity']/rows[i]['pretrade_equity']-1
    rows[-2]['net_interval_return']=rows[-1]['posttrade_equity']/rows[-2]['pretrade_equity']-1
    q=[r['net_interval_return'] for r in rows[:-1]]
    assert all(math.isfinite(x) and x>-1 for x in q)
    assert abs(5000*math.prod(1+x for x in q)-rows[-1]['posttrade_equity'])<=max(1e-8,1e-10*rows[-1]['posttrade_equity'])
    return rows

def period(rows,first,last):
    terminal=last==len(rows)-2;start=rows[first]['pretrade_equity']
    end=rows[-1]['posttrade_equity'] if terminal else rows[last+1]['pretrade_equity']
    hold=rows[first:last+1];trades=hold+([rows[-1]] if terminal else [])
    q=[r['net_interval_return'] for r in hold];sd=statistics.pstdev(q);mean=statistics.fmean(q)
    assert abs(start*math.prod(1+x for x in q)-end)<=max(1e-8,1e-10*end)
    peak=start;dd=0.
    for value in [start]+[v for r in trades for v in (r['pretrade_equity'],r['posttrade_equity'])]+[end]:
        peak=max(peak,value);dd=max(dd,1-value/peak)
    lastrow=rows[-1] if terminal else rows[last]
    return {'start_equity_USD':start,'end_equity_USD':end,'net_USD':end-start,
      'total_return':end/start-1,'CAGR':(end/start)**(365/len(q))-1,
      'annualized_volatility':sd*math.sqrt(365),'Sharpe':math.sqrt(365)*mean/sd if sd>0 else None,
      'maximum_drawdown':dd,'all_cost_USD':math.fsum(r['cost_USD'] for r in trades),
      'turnover':math.fsum(r['reference_trade_USD']/r['pretrade_equity'] for r in trades),
      'average_exposure':statistics.fmean(r['actualweight'] for r in hold),
      'min_exposure':min(r['actualweight'] for r in hold),'max_exposure':max(r['actualweight'] for r in hold),
      'nonzero_trade_count':sum(r['trade_BTC']!=0 for r in trades),
      'zero_volume_no_fill_count':sum(r['zero_volume_no_fill'] for r in trades),
      'zero_reference_volume_rows':sum(r['reference_volume']==0 for r in trades),
      'start_BTC':rows[first]['pretrade_units'],'start_cash':rows[first]['pretrade_cash'],
      'end_BTC':lastrow['posttrade_units'],'end_cash':lastrow['posttrade_cash'],
      'first_holding_date':rows[first]['date'],'last_holding_date':rows[last]['date'],
      'end_valuation_date':rows[last+1]['date'],'intervals':len(q),'terminal_fee_included':terminal}

def metrics(rows):
    years={}
    for y in sorted({r['date'][:4] for r in rows[:-1]}):
        ix=[i for i,r in enumerate(rows[:-1]) if r['date'][:4]==y];years[y]=period(rows,ix[0],ix[-1])
    return {'overall':period(rows,0,len(rows)-2),'all_six_years':years,
      'terminal_liquidated':rows[-1]['posttrade_units']==0,'residual_BTC':rows[-1]['posttrade_units']}

def synthetic_points(dates,volumes,targets):
    return [{'date':d,'decision_UTC':d+'T00:10:00Z','feature_cutoff':'SYNTHETIC',
             'P':100.+i*10,'reference_volume':v,'annual_f_y':w,
             'annual_generation_date':d[:4]+'-01-01'} for i,(d,v,w) in enumerate(zip(dates,volumes,targets))]

def fixtures():
    # Synthetic-only data, no old account state. Both independently enter from cash.
    p=synthetic_points(['2020-01-01','2020-01-02','2020-12-31','2021-01-01','2021-01-02'],
                       [1.,1.,1.,1.,1.],[.6,.6,.6,.2,.2])
    a=ledger(p,'A',25);b=ledger(p,'B',25)
    assert a[0]['pretrade_cash']==b[0]['pretrade_cash']==5000
    assert a[0]['pretrade_units']==b[0]['pretrade_units']==0
    for k in ('posttrade_cash','posttrade_units','cost_USD'):assert a[0][k]==b[0][k]
    assert a[0]['cost_USD']>0 and a[-1]['cost_USD']>0 and b[-1]['cost_USD']>0
    for i in (1,2):assert a[i]['posttrade_units']==a[0]['posttrade_units'] and a[i]['posttrade_cash']==a[0]['posttrade_cash']
    assert all(b[i]['posttrade_units']==b[0]['posttrade_units'] and b[i]['posttrade_cash']==b[0]['posttrade_cash'] for i in (1,2,3))
    assert a[3]['trade_BTC']!=0 and b[3]['trade_BTC']==0
    assert math.fsum(r['cost_USD'] for r in b)==b[0]['cost_USD']+b[-1]['cost_USD']
    assert a[1]['cost_USD']==a[2]['cost_USD']==b[1]['cost_USD']==b[2]['cost_USD']==b[3]['cost_USD']==0
    assert a[3]['pretrade_cash']==a[2]['posttrade_cash'] and a[3]['pretrade_units']==a[2]['posttrade_units']
    for rr in (a,b):
        assert rr[-1]['posttrade_units']==0 and rr[-1]['net_interval_return'] is None
        assert rr[-2]['net_interval_return']==rr[-1]['posttrade_equity']/rr[-2]['pretrade_equity']-1
    q=synthetic_points(['2020-01-01','2020-01-02','2021-01-01','2021-01-02','2021-01-03'],
                       [0.,0.,0.,1.,1.],[.6,.6,.3,.3,.3])
    ar=ledger(q,'A',25);br=ledger(q,'B',25)
    assert ar[2]['newyear_replaced_pending'] and br[2]['newyear_replaced_pending']
    assert ar[3]['target_if_attempt']==br[3]['target_if_attempt']==.3
    assert ar[3]['posttrade_units']==br[3]['posttrade_units']
    q[-1]['reference_volume']=0
    fail=ledger(q,'A',25);assert fail[-1]['posttrade_units']>0 and fail[-1]['cost_USD']==0
    q=synthetic_points(['2020-12-31','2021-01-01'],[0.,1.],[.6,.3])
    terminal=ledger(q,'A',25);assert terminal[-1]['target_if_attempt']==0 and terminal[-1]['posttrade_units']==0
    # Contiguous synthetic daily boundary allows actual annual-statistics checks.
    q=synthetic_points(['2020-12-30','2020-12-31','2021-01-01','2021-01-02'],[1.]*4,[.6,.6,.3,.3])
    rr=ledger(q,'A',25);old=period(rr,0,1);new=period(rr,2,2)
    assert old['end_equity_USD']==new['start_equity_USD']==rr[2]['pretrade_equity']
    assert old['end_BTC']==new['start_BTC'] and old['end_cash']==new['start_cash']
    assert not old['terminal_fee_included'] and new['terminal_fee_included']
    return {'status':'PASS_NONMARKET_SYNTHETIC','checks':['fresh5000cash_zeroBTC_not_copied',
      'same_cost_A_B_initial_allocation','fixed_units_cash_carry','A_annual_event_B_no_rebalance',
      'pending_multiday_newyear_replacement','terminal_priority','zero_volume_terminal_invalid',
      'year_pretrade_boundary_inheritance','ordinary_and_last_return_fee_once'],
      'real_market_accounts_or_performance_created':False}

def reference_points(cfg):
    result={};identities={}
    for cost,ref in cfg['data']['source_ledgers'].items():
        identities[ref['path']]=fp(ref['path']);assert identities[ref['path']]['sha256']==ref['sha256']
        selected=[]
        with Path(ref['path']).open(newline='') as f:
            reader=csv.DictReader(f);assert all(k in reader.fieldnames for k in SOURCE_KEYS)
            for r in reader:
                if '2020-01-01'<=r['date']<='2025-12-31':selected.append({k:r[k] for k in SOURCE_KEYS})
        assert len(selected)==2192
        for i,r in enumerate(selected):
            day=date.fromisoformat(r['date'])
            assert r['decision_UTC']==r['date']+'T00:10:00Z'
            assert r['feature_cutoff']==(day-timedelta(days=2)).isoformat()
            if i:assert day-date.fromisoformat(selected[i-1]['date'])==timedelta(days=1)
            assert all(math.isfinite(float(r[k])) for k in ('P','reference_volume','annual_f_y'))
            assert float(r['P'])>0 and float(r['reference_volume'])>=0 and 0<=float(r['annual_f_y'])<=1
            assert r['annual_generation_date']==r['date'][:4]+'-01-01'
        assert selected[0]['date']=='2020-01-01' and selected[-1]['date']=='2025-12-31'
        generations=[r for r in selected if r['date'].endswith('-01-01')];assert len(generations)==6
        assert selected[0]['annual_f_y']=='0.7853985165876642'
        for year in range(2020,2026):
            yr=[r for r in selected if r['date'].startswith(str(year))]
            assert all(r['annual_f_y']==yr[0]['annual_f_y'] for r in yr)
        result[cost]=selected
    assert result['25']==result['50'],'SOURCE_REFERENCE_EVENT_MISMATCH'
    return result['25'],identities

def prepare():
    au,cfg,inputs=fixed();h=health();fx=fixtures();records,ids=reference_points(cfg);inputs.update(ids)
    p=A/'reference-inputs.csv'
    with p.open('x',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(SOURCE_KEYS));wr.writeheader();wr.writerows(records)
    save('health.json',h);save('synthetic-fixtures.json',fx)
    save('preflight.json',{'UTC':utc(),'status':'STOPPED_BEFORE_FORMAL_FRESH_A_B_ACCOUNTS',
      'inputs':inputs,'source_inputs':{str(p):fp(p) for p in (D/'restart_adapter.py',D/'supervise.py')},
      'prepared_references':{str(p):fp(p)},'points':2192,'intervals':2191,
      'first_UTC':records[0]['decision_UTC'],'last_UTC':records[-1]['decision_UTC'],
      'initial_target':records[0]['annual_f_y'],'initial_cutoff':records[0]['feature_cutoff'],
      'frozen_instruction_dates':[r['date'] for r in records if r['date'].endswith('-01-01')],
      'source_fields_whitelist':list(SOURCE_KEYS),'old_wealth_units_fee_return_fields_loaded_as_state':False,
      'real_market_accounts_or_performance_created':False,
      'git_markers':{str(p):(p/'.git').exists() for p in (D,D.parent,D.parent.parent,D.parent.parent.parent)}})
    print(json.dumps({'UTC':utc(),'PID':os.getpid(),'status':'STOPPED_BEFORE_FORMAL_FRESH_A_B_ACCOUNTS'}),flush=True)

def run(gate_path):
    au,cfg,_=fixed();health();gate=read(gate_path);pre=read(A/'preflight.json')
    assert gate.get('allow_formal_restart2020') is True
    assert gate['source_inputs']==pre['source_inputs']
    for group in ('inputs','source_inputs','prepared_references'):
        for path,identity in pre[group].items():assert fp(path)==identity,'PREPARED_IDENTITY:'+path
    for path,identity in gate.get('inputs',{}).items():assert fp(path)==identity,'GATE_IDENTITY:'+path
    with (D/'formal-restart2020-started.lock').open('x') as f:
        json.dump({'UTC':utc(),'PID':os.getpid(),'gate':str(gate_path),'gate_identity':fp(gate_path)},f)
    save('configuration-before-accounts.seal.json',{'UTC':utc(),'inputs':pre['inputs'],
      'prepared_references':pre['prepared_references'],'sources':pre['source_inputs'],'gate':fp(gate_path)})
    points=[]
    with (A/'reference-inputs.csv').open(newline='') as f:
        for r in csv.DictReader(f):points.append({k:float(v) if k in ('P','reference_volume','annual_f_y') else v for k,v in r.items()})
    accounts={};files=[];common_checks={}
    for cost in (25,50):
        accounts[str(cost)]={}
        for method in ('A','B'):
            rows=ledger(points,method,cost);accounts[str(cost)][method]=rows
            path=A/f'{method}-fresh2020-{cost}bps-ledger.csv'
            with path.open('x',newline='') as f:
                wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
            files.append(path)
        a,b=accounts[str(cost)]['A'],accounts[str(cost)]['B']
        first=next(i for i,r in enumerate(a) if r['allocation_completed'] and not r['terminal'])
        for key in ('pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','cost_USD'):
            assert a[first][key]==b[first][key],'INITIAL_A_B_MATCH:'+key
        subsequent=next((i for i,r in enumerate(a) if i>first and not r['terminal'] and r['trade_BTC']!=0),len(a)-1)
        for i in range(subsequent):
            assert a[i]['pretrade_equity']==b[i]['pretrade_equity'] and a[i]['posttrade_equity']==b[i]['posttrade_equity']
        assert a[subsequent]['pretrade_equity']==b[subsequent]['pretrade_equity']
        common_checks[str(cost)]={'first_allocation':a[first]['decision_UTC'],
          'first_subsequent_A_nonzero_reallocation_or_terminal':a[subsequent]['decision_UTC'],
          'same_path_before_that_trade':True}
    save('all-four-accounts-before-scoring.seal.json',{'UTC':utc(),'ledgers':{str(p):fp(p) for p in files},
      'common_initial_and_prereallocation_checks':common_checks,'scoring_started':False})
    result={cost:{method:metrics(rows) for method,rows in pairs.items()} for cost,pairs in accounts.items()}
    ratios={};risk_ok=True;valid=True
    for cost,m in result.items():
        va,vb=m['A']['overall']['annualized_volatility'],m['B']['overall']['annualized_volatility']
        ratio=va/vb if vb>0 else None;ratios[cost]=ratio;risk_ok &= ratio is not None and .8<=ratio<=1.2
        valid &= m['A']['terminal_liquidated'] and m['B']['terminal_liquidated']
    a,b=result['25']['A']['overall'],result['25']['B']['overall'];s,t=result['50']['A']['overall'],result['50']['B']['overall']
    defined=all(x['Sharpe'] is not None for x in (a,b,s,t))
    gates={'terminal_valid':bool(valid),'both_risk_ratios_qualified':bool(risk_ok),
      'A25_terminal_positive_and_greater_B':a['end_equity_USD']>5000 and a['end_equity_USD']>b['end_equity_USD'],
      'A25_Sharpe_ge_B_plus020':defined and a['Sharpe']>=b['Sharpe']+.20,
      'A25_DD_not_larger':a['maximum_drawdown']<=b['maximum_drawdown'],
      'A50_terminal_positive_and_greater_B':s['end_equity_USD']>5000 and s['end_equity_USD']>t['end_equity_USD'],
      'A50_Sharpe_not_lower':defined and s['Sharpe']>=t['Sharpe'],
      'A50_DD_not_larger':s['maximum_drawdown']<=t['maximum_drawdown']}
    status=('TECHNICALLY_INVALID' if not valid else 'INCONCLUSIVE_RISK_MISMATCH' if not risk_ok else
            'DESCRIPTIVE_LATER_START_ADVANTAGE' if all(gates.values()) else 'NOT_SUPPORTED_THIS_DIAGNOSTIC')
    path=save('evaluation-results.json',{'UTC':utc(),'status':status,'metrics':result,
      'risk_ratios_A_over_B':ratios,'gates':gates,'same_path_before_subsequent_A_reallocation':common_checks,
      'all_accounts_fresh5000cash_zeroBTC':True,'old_wealth_normalization_or_state_copy':False,
      'all_six_years_retained':True,'fresh_OOS':False,'models_or_statistics_search':False,
      'actual_execution_costs_capacity_and_PIT':'UNKNOWN','actual_trades':0,'wealth_goal_achieved':False})
    current={p:fp(p) for p in pre['inputs']};assert current==pre['inputs']
    save('final-result.seal.json',{'UTC':utc(),'result':{str(path):fp(path)},'unchanged_inputs':current,
      'single_formal_claim':fp(D/'formal-restart2020-started.lock')})
    print(json.dumps({'UTC':utc(),'status':status,'formal_unit_count':1}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('prepare','run'));ap.add_argument('--approval');args=ap.parse_args()
    if args.stage=='prepare':prepare()
    else:
        assert args.approval
        run(Path(args.approval))
