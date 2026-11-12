"""Stdlib, one fixed accounting decision; no old-script imports or execution on import."""
from pathlib import Path
from datetime import datetime,date,timedelta,timezone
import csv,hashlib,json,math,statistics,sys,time,os
D=Path(__file__).resolve().parent

def utc():return datetime.now(timezone.utc).isoformat()
def identity(p):
    p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def save(name,v):
    p=D/name
    with p.open('x') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
    guard();return identity(p)
def read(p):return json.loads(Path(p).read_text())
def guard():
    assert datetime.now(timezone.utc)<datetime(2026,10,21,4,45,tzinfo=timezone.utc),'WORK_DEADLINE'
    assert sum(p.stat().st_size for p in D.rglob('*') if p.is_file())<16*1024**2,'DISK_CAP'
def close(a,b):return abs(a-b)<=max(1e-8,1e-10*max(abs(a),abs(b),1))
def inputs(cfg):
    out={}
    for k,v in cfg['inputs'].items():
        q=identity(v['path']);assert q['sha256']==v['sha256'],k+'_IDENTITY';out[k]=q
    return out

def rebalance(cash,units,p,target,fee):
    assert p>0 and 0<=target<=1 and 0<=fee<1 and cash>=0 and units>=0
    V=cash+units*p;assert V>0
    diff=target*V-units*p
    sign=1 if diff>0 else -1 if diff<0 else 0
    x=diff/(1+sign*target*fee)
    cost=abs(x)*fee;u=units+x/p;c=cash-x-cost
    if abs(c)<1e-10:c=0.
    if abs(u)<1e-14:u=0.
    W=c+u*p
    assert c>=0 and u>=0 and close(V-W,cost) and close(c,cash-x-cost),'SELF_FINANCING'
    assert close(u*p/W,target),'POST_FEE_TARGET'
    return c,u,x,cost

def account(points,cash,units,target,fee,label):
    rows=[]
    for i,p in enumerate(points):
        terminal=i==len(points)-1;C,Q=cash,units;V=C+Q*p['price']
        action='TERMINAL_LIQUIDATION' if terminal else 'ANNUAL_UPDATE' if i==0 and target is not None else 'HOLD'
        t=0. if terminal else target if i==0 else None
        if t is None:x=cost=0.
        else:cash,units,x,cost=rebalance(C,Q,p['price'],t,fee)
        W=cash+units*p['price']
        assert close(W,V-cost) and close(cash,C-x-cost) and close(units,Q+x/p['price'])
        rows.append({'date':p['date'],'decision_UTC':p['date']+'T00:10:00Z','group':label,'fee_rate':fee,
          'price':p['price'],'volume':p['volume'],'action':action,'target_if_action':t,
          'pretrade_cash':C,'pretrade_units':Q,'pretrade_equity':V,'pretrade_exposure':Q*p['price']/V,
          'posttrade_cash':cash,'posttrade_units':units,'posttrade_equity':W,'posttrade_exposure':units*p['price']/W,
          'signed_nominal_USD':x,'fee_USD':cost,'net_interval_return':None})
    for i in range(len(rows)-1):
        end=rows[-1]['posttrade_equity'] if i==len(rows)-2 else rows[i+1]['pretrade_equity']
        rows[i]['net_interval_return']=end/rows[i]['pretrade_equity']-1
    rr=[r['net_interval_return'] for r in rows[:-1]]
    assert close(rows[0]['pretrade_equity']*math.prod(1+r for r in rr),rows[-1]['posttrade_equity'])
    assert rows[-1]['posttrade_units']==0
    assert all(math.isfinite(x) and x>-1 for x in rr)
    return rows

def metric(rows):
    rr=[r['net_interval_return'] for r in rows[:-1]];sd=statistics.pstdev(rr);peak=rows[0]['pretrade_equity'];dd=0
    for r in rows:
        for v in (r['pretrade_equity'],r['posttrade_equity']):peak=max(peak,v);dd=max(dd,1-v/peak)
    fees=math.fsum(r['fee_USD'] for r in rows);entry=rows[0]['fee_USD'];exit=rows[-1]['fee_USD']
    market=rows[0]['posttrade_units']*(rows[-1]['price']-rows[0]['price'])
    assert close(rows[-1]['posttrade_equity'],5000+market-fees),'ATTRIBUTION_IDENTITY'
    return {'terminal_cash_USD':rows[-1]['posttrade_cash'],'net_USD':rows[-1]['posttrade_cash']-5000,
      'annualized_population_volatility':sd*math.sqrt(365),'Sharpe':statistics.fmean(rr)/sd*math.sqrt(365) if sd>0 else None,
      'maximum_drawdown':dd,'fees_USD':fees,'entry_fee_USD':entry,'exit_fee_USD':exit,
      'reference_traded_notional_USD':math.fsum(abs(r['signed_nominal_USD']) for r in rows),
      'trade_count':sum(r['signed_nominal_USD']!=0 for r in rows),'no_fill_count':0,
      'exposure_before_update':rows[0]['pretrade_exposure'],'exposure_after_update':rows[0]['posttrade_exposure'],
      'mean_holding_exposure':statistics.fmean(r['posttrade_exposure'] for r in rows[:-1]),
      'terminal_preliquidation_exposure':rows[-1]['pretrade_exposure'],'terminal_postliquidation_exposure':rows[-1]['posttrade_exposure'],
      'post_update_units':rows[0]['posttrade_units'],'post_update_cash':rows[0]['posttrade_cash'],
      'BTC_price_change_USD':rows[-1]['price']-rows[0]['price'],'inventory_mark_to_market_USD':market,
      'daily_intervals':len(rr),'return_product_reconciled':True,'attribution_identity':'terminal=5000+post_update_units*(PT-P0)-entry_fee-exit_fee'}

def score(ledgers):
    allmetrics={k:metric(v) for k,v in ledgers.items()};costs={};risk=True;candidate=True;sep=True
    for bps in (50,100):
        a=allmetrics[f'A-{bps}'];ratios={};comparisons={}
        for group in ('B','C'):
            z=allmetrics[f'{group}-{bps}'];den=z['annualized_population_volatility']
            ratio=a['annualized_population_volatility']/den if den>0 else None;ratios[group]=ratio
            risk=risk and ratio is not None and math.isfinite(ratio) and .8<=ratio<=1.2
            tol=max(1e-6,1e-10*max(abs(a['terminal_cash_USD']),abs(z['terminal_cash_USD']),1))
            diff=a['terminal_cash_USD']-z['terminal_cash_USD'];ddok=a['maximum_drawdown']<=z['maximum_drawdown']+1e-10
            candidate=candidate and diff>tol and ddok
            marketdiff=a['inventory_mark_to_market_USD']-z['inventory_mark_to_market_USD'];feediff=a['fees_USD']-z['fees_USD']
            assert close(diff,marketdiff-feediff)
            comparisons[group]={'A_minus_baseline_USD':diff,'wealth_tolerance_USD':tol,'A_strictly_leads':diff>tol,
              'A_drawdown_not_worse':ddok,'inventory_market_contribution_difference_USD':marketdiff,'fee_difference_USD':feediff,
              'attribution':'A-minus-baseline = post-update inventory price contribution difference minus fee difference'}
            if close(a['post_update_units'],z['post_update_units']) and close(a['post_update_cash'],z['post_update_cash']):sep=False
        candidate=candidate and a['net_USD']>max(1e-6,1e-10*a['terminal_cash_USD'])
        costs[str(bps)]={'A_to_baseline_volatility_ratios':ratios,'comparisons':comparisons}
    label='INCONCLUSIVE_RISK_MISMATCH' if not risk else 'NO_RULE_SEPARATION' if not sep else 'A_ONE_DECISION_CANDIDATE' if candidate else 'ONE_DECISION_NOT_SUPPORTED_OR_RISK_TRADEOFF'
    return {'classification':label,'technical_accounting':'PASS','risk_comparable_all_four_ratios':risk,'rule_separation_all_comparisons':sep,
      'all_six_accounts':allmetrics,'per_cost':costs,'business_net_edge':'BUSINESS_NET_EDGE_UNVERIFIED',
      'scope':'ONE_ANNUAL_DECISION_CONDITIONAL_HISTORICAL_HOLDOUT; INHERITED_INVENTORY; PROXY_FILLS_NOT_REAL_FILLS',
      'personal_funding_FX_maintenance_software_electricity_labor_tax_costs':'UNKNOWN','execution_capacity':'NOT_VALIDATED',
      'exposure_convention':'mean of 288 post-action holding-start exposures; pre-update, post-update, terminal-pre and terminal-post separately',
      'MDD_convention':'initial equity and all pre/post action marks; DD tolerance=1e-10',
      'return_convention':'288 simple net interval returns use starting pre-update 5000; entry fee in first interval and terminal fee in last',
      'no_alpha_or_prediction_or_statistical_significance_claim':True}

def synthetic():
    results=[]
    for target in (0.,.2,.7,1.):
        for f in (.005,.01):
            c,u,x,cost=rebalance(3000,20,100,target,f)
            assert close(c+u*100+cost,5000)
            assert (x>0)==(target>.4) if target!=.4 else x==0
            results.append({'case':'inherited_buy_or_sell','target':target,'fee':f,'cash':c,'units':u,'cost':cost})
    c,u,x,cost=rebalance(3000,20,100,.4,.01);assert x==cost==0 and c==3000 and u==20
    pts=[{'date':'SYNTHETIC-'+str(i),'price':p,'volume':1} for i,p in enumerate((100.,110.,90.,120.))]
    led={}
    for bps in (50,100):
        for label,target in [('A',.6),('B',None),('C',.8)]:
            rows=account(pts,3000.,20.,target,bps/10000,label);led[f'{label}-{bps}']=rows
            assert len([r for r in rows[:-1] if r['net_interval_return'] is not None])==3
            assert rows[1]['fee_USD']==rows[2]['fee_USD']==0
            assert close(5000*(1+rows[0]['net_interval_return']),rows[1]['pretrade_equity'])
            if label=='B':assert rows[0]['fee_USD']==0
            else:assert rows[0]['fee_USD']>0
            assert rows[-1]['fee_USD']>0
    score(led)
    for scenario,prices in [('FLAT',(100.,100.,100.,100.)),('UP',(100.,105.,110.,120.)),('DOWN',(100.,95.,90.,80.))]:
        pts=[{'date':'SYNTHETIC-'+str(i),'price':p,'volume':1} for i,p in enumerate(prices)]
        for bps in (50,100):
            for group,target in [('A',.6),('B',None),('C',.8)]:
                rr=account(pts,3000.,20.,target,bps/10000,group);m=metric(rr)
                assert close(5000*math.prod(1+r['net_interval_return'] for r in rr[:-1]),m['terminal_cash_USD'])
                if scenario=='FLAT':assert close(m['net_USD'],-m['fees_USD'])
                results.append({'case':scenario,'group':group,'fee_bps':bps,'terminal':m['terminal_cash_USD'],'fees':m['fees_USD'],'return_product_reconciled':True})
    return {'synthetic_only':True,'no_market_prices_used':True,'cases':results,'checks':['buy','sell','zero trade','target0','target1','both costs','self financing','cash/units nonnegative','fee once','first interval entry fee','last interval exit fee','return product','six-account attribution'],'passed':True}

def prepare(cfg):
    ids=inputs(cfg)
    with open(cfg['inputs']['seed']['path']) as f:
        rr=list(csv.DictReader(f));r=rr[-1];prev=rr[-2]
    assert r['date']=='2025-12-31' and r['terminal']=='True'
    assert r['pretrade_units']==cfg['seed']['units'] and r['pretrade_cash']==cfg['seed']['cash']
    assert float(prev['posttrade_units'])==float(r['pretrade_units']) and float(prev['posttrade_cash'])==float(r['pretrade_cash'])
    assert float(r['posttrade_units'])==0
    warm=[];dates=[]
    with open(cfg['inputs']['daily']['path']) as f:
        for row in csv.DictReader(f):
            d=row['date']
            if '2025-10-31'<=d<='2025-12-30':
                assert math.isfinite(float(row['close'])) and float(row['close'])>0;warm.append(d)
            if '2026-01-01'<=d<='2026-10-16':dates.append(d) # date only, do not parse any price or performance
    expected=lambda a,n:[(date.fromisoformat(a)+timedelta(days=i)).isoformat() for i in range(n)]
    assert warm==expected('2025-10-31',61) and dates==expected('2026-01-01',289)
    s=save('synthetic-checks.json',synthetic())
    save('preflight.json',{'UTC':utc(),'status':'PREPARATION_PASS_NO_MARKET_CALCULATION','inputs':ids,'synthetic':s,
      'warmup_dates_validated':61,'market_dates_only_validated':289,'2026_price_or_performance_parsed':False,
      '2026_target_computed':False,'seed_row_identity':{k:r[k] for k in ('date','terminal','pretrade_cash','pretrade_units','posttrade_cash','posttrade_units')},
      'code':identity(__file__),'config':identity(D/'config.json'),'actual_model':'UNKNOWN','actual_effort':'UNKNOWN'})

def formal(cfg,gatepath):
    guard();gate=read(gatepath)
    assert gate['status']=='RELEASED_ONCE_COMMON_INVENTORY_2026' and gate['code_sha256']==identity(__file__)['sha256']
    assert gate['config_sha256']==identity(D/'config.json')['sha256']
    ids=inputs(cfg)
    for name in ('code_sha256','config_sha256'):assert isinstance(gate[name],str)
    with (D/'formal-started.json').open('x') as f:json.dump({'UTC':utc(),'PID':os.getpid(),'gate':identity(gatepath),'formal_attempts':1},f)
    save('pre-market-seal.json',{'UTC':utc(),'code':identity(__file__),'config':identity(D/'config.json'),'gate':identity(gatepath),'inputs':ids,'preflight':identity(D/'preflight.json')})
    closes=[];warmdates=[]
    with open(cfg['inputs']['daily']['path']) as f:
        for row in csv.DictReader(f):
            if '2025-10-31'<=row['date']<='2025-12-30':closes.append(float(row['close']));warmdates.append(row['date'])
    assert len(closes)==61 and all(math.isfinite(v) and v>0 for v in closes)
    r=[closes[i+1]/closes[i]-1 for i in range(60)];sigma=max(statistics.pstdev(r),1e-6);target=min(1.,.4/(math.sqrt(365)*sigma))
    save('target-before-market-seal.json',{'UTC':utc(),'warmup_dates':warmdates,'warmup_closes':closes,'simple_returns':r,'population_sigma_floored':sigma,'A_f2026':target,'C_k':cfg['fixed_k'],'information_cutoff':'2025-12-30=e-2','2026_prices_not_yet_parsed':True})
    if abs(target-cfg['fixed_k'])<=1e-10:
        save('structural-terminal.json',{'UTC':utc(),'classification':'NO_RULE_SEPARATION','formal_attempts':1,'market_prices_parsed':False});return
    points=[]
    with open(cfg['inputs']['daily']['path']) as f:
        for row in csv.DictReader(f):
            if '2026-01-01'<=row['date']<='2026-10-16':
                p=float(row['price']);v=float(row['volume']);assert math.isfinite(p) and p>0 and math.isfinite(v) and v>=0
                points.append({'date':row['date'],'price':p,'volume':v})
    assert len(points)==289 and points[0]['date']=='2026-01-01' and points[-1]['date']=='2026-10-16'
    assert all((date.fromisoformat(points[i+1]['date'])-date.fromisoformat(points[i]['date'])).days==1 for i in range(288))
    assert points[0]['volume']>0 and points[-1]['volume']>0,'ENDPOINT_VOLUME_STOP'
    q=float(cfg['seed']['units']);c=float(cfg['seed']['cash']);scale=5000/(q*points[0]['price']+c);q*=scale;c*=scale
    save('common-seed-and-market-inputs.json',{'UTC':utc(),'scale':scale,'units':q,'cash':c,'equity':q*points[0]['price']+c,'source':'pre-liquidation snapshot rescaled at P0; counterfactual not actual account continuation','points':points})
    led={};seal={}
    for bps in cfg['costs_bps']:
        for label,t in [('A',target),('B',None),('C',cfg['fixed_k'])]:
            guard();key=f'{label}-{bps}';rows=account(points,c,q,t,bps/10000,label);led[key]=rows
            p=D/(key+'-ledger.csv')
            with p.open('x',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            seal[key]=identity(p)
    save('all-six-ledgers-seal.json',{'UTC':utc(),'ledgers':seal,'target':identity(D/'target-before-market-seal.json'),'common_seed':identity(D/'common-seed-and-market-inputs.json'),'inputs_rechecked':inputs(cfg),'code':identity(__file__),'all_six_sealed_before_scoring':True})
    result=score(led);result.update({'UTC':utc(),'formal_attempts':1,'common_seed_units':q,'common_seed_cash':c,'A_f2026':target,'C_k':cfg['fixed_k']})
    save('results.json',result)
    save('final-result-seal.json',{'UTC':utc(),'result':identity(D/'results.json'),'six_ledgers':identity(D/'all-six-ledgers-seal.json'),'target':identity(D/'target-before-market-seal.json'),'common_seed':identity(D/'common-seed-and-market-inputs.json'),'formal_attempts':1})

if __name__=='__main__':
    guard();cfg=read(D/'config.json')
    if sys.argv[1:] == ['--prepare']:prepare(cfg)
    elif len(sys.argv)==3 and sys.argv[1]=='--formal':formal(cfg,sys.argv[2])
    else:raise SystemExit('EXACT_MODE_REQUIRED')
