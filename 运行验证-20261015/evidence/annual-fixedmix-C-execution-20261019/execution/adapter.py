"""Offline C fixed annual mix. Stdlib only; never imports/executes old adapters.
Transaction and descriptive metric functions reused verbatim from sealed restart_adapter.py.
Only ledger_C creates a new account, and only after explicit formal gate.
"""
from pathlib import Path
from datetime import date,datetime,timedelta,timezone
import argparse,csv,hashlib,json,math,os,statistics,sys,time,resource
D=Path(__file__).resolve().parent.parent
A=D/'artifacts'
OLD=D.parent/'annual-restart2020-execution-20261018'
PRIOR=D.parent/'risk-scaled-vs-annual-execution-20261017'
K=0.7853985165876642
KEYS=('date','decision_UTC','feature_cutoff','P','reference_volume','annual_f_y','annual_generation_date')
def utc():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def fp(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return {'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def save(p,obj):
    with Path(p).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def deadline():
    if globals().get('FORMAL_START') is not None:assert time.monotonic()-FORMAL_START<600,'COMPUTE_LIMIT'

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

def ledger_C(points,bps):
    cash,units=5000.,0.;pending=False;entered=False;frozen=None;generation=None;rows=[]
    for i,p in enumerate(points):
        if i%128==0:deadline()
        terminal=i==len(points)-1;newyear=p['date'].endswith('-01-01');replaced=False
        if not terminal and (i==0 or newyear):
            replaced=pending;frozen=K;generation=p['date'][:4]+'-01-01';pending=True
        before=pending;attempt=True if terminal else pending
        target=0. if terminal else frozen if attempt else None
        cash,units,detail=transaction(cash,units,p['P'],p['reference_volume'],target,attempt,bps)
        if detail['allocation_completed']:
            pending=False
            if not terminal:entered=True
        rows.append({'date':p['date'],'decision_UTC':p['decision_UTC'],'feature_cutoff':p['feature_cutoff'],
          'P':p['P'],'reference_volume':p['reference_volume'],'method':'C','cost_bps':bps,
          'frozen_target':frozen,'generation_date':generation,'pending_before':before,'pending_after':pending,
          'newyear_replaced_pending':replaced,'attempt':attempt,'target_if_attempt':target,
          'entered_after_row':entered,'terminal':terminal,**detail,'net_interval_return':None})
    assert len(rows)>=2
    for i in range(len(rows)-1):rows[i]['net_interval_return']=rows[i+1]['pretrade_equity']/rows[i]['pretrade_equity']-1
    rows[-2]['net_interval_return']=rows[-1]['posttrade_equity']/rows[-2]['pretrade_equity']-1
    assert all(math.isfinite(r['net_interval_return']) and r['net_interval_return']>-1 for r in rows[:-1])
    assert math.isclose(5000*math.prod(1+r['net_interval_return'] for r in rows[:-1]),rows[-1]['posttrade_equity'],rel_tol=1e-10,abs_tol=1e-8)
    return rows

def fixture_points(ds,vs,ps):
    return [dict(date=d,decision_UTC=d+'T00:10:00Z',feature_cutoff='SYNTHETIC',P=p,reference_volume=v,annual_f_y=.1,annual_generation_date=d[:4]+'-01-01') for d,v,p in zip(ds,vs,ps)]
def fixtures():
    p=fixture_points(['2020-12-30','2020-12-31','2021-01-01','2021-01-02'],[1]*4,[100,150,200,210])
    reports=[]
    for bps in (25,50):
        r=ledger_C(p,bps)
        assert r[0]['pretrade_cash']==5000 and r[0]['pretrade_units']==0
        assert r[1]['posttrade_cash']==r[0]['posttrade_cash'] and r[1]['posttrade_units']==r[0]['posttrade_units']
        assert r[1]['cost_USD']==0 and r[1]['actualweight']!=K
        assert r[2]['target_if_attempt']==K and r[2]['trade_BTC']<0 and math.isclose(r[2]['actualweight'],K)
        assert r[-1]['posttrade_units']==0 and r[-1]['cost_USD']>0 and r[-1]['net_interval_return'] is None
        assert r[-2]['net_interval_return']==r[-1]['posttrade_equity']/r[-2]['pretrade_equity']-1
        old=period(r,0,1);new=period(r,2,2)
        assert old['end_equity_USD']==new['start_equity_USD']==r[2]['pretrade_equity']
        q=fixture_points(['2020-12-30','2020-12-31','2021-01-01','2021-01-02','2021-01-03'],[0,0,0,1,1],[100,200,150,120,130])
        rr=ledger_C(q,bps)
        assert all(x['posttrade_cash']==5000 and x['posttrade_units']==0 and x['cost_USD']==0 for x in rr[:3])
        assert rr[2]['newyear_replaced_pending'] and rr[3]['allocation_completed'] and rr[3]['target_if_attempt']==K
        q[-1]['reference_volume']=0;rr=ledger_C(q,bps)
        assert rr[-1]['posttrade_units']>0 and rr[-1]['cost_USD']==0 and rr[-1]['zero_volume_no_fill']
        t=ledger_C(fixture_points(['2020-12-31','2021-01-01'],[0,1],[100,150]),bps)
        assert t[-1]['target_if_attempt']==0 and t[-1]['posttrade_units']==0 and t[-1]['cost_USD']==0
        # Explicit buy and sell conservation, including zero-delta fixed weight.
        for units,cash,target in [(0,5000,K),(30,1000,.3),(10,1000,.8),(10,1000,.5)]:
            c,u,x=transaction(cash,units,100,1,target,True,bps)
            assert math.isclose(u*100/(c+u*100),target,abs_tol=1e-14)
        reports.append({'bps':bps,'passed':True})
    return dict(status='PASS_SYNTHETIC_ONLY',cases=['fresh_cash','buy_sell_zero_delta_self_finance','exact_units_cash_carry_and_drift','annual_fixed_k_not_A_dynamic_or_B_static','zero_volume_pending_retry','newyear_pending_replacement','terminal_priority','terminal_zero_volume_invalid','annual_pretrade_boundary','terminal_fee_once'],costs=reports,real_market_C_accounts_created=0)

def checked_sources():
    final=OLD/'review/final-review.json'
    # Exact legacy seals anchored by already-reviewed SHA256, not self-asserted current identities.
    anchors={'artifacts/configuration-before-accounts.seal.json':'0162b1169dbaeea9eed2220d0a0857f41f716441b8655952a68ae7dcbd0d79df','artifacts/all-four-accounts-before-scoring.seal.json':'0602cb50f55da19a69878e38cde6c83281910e1a7d39800914dd472eadc6fb29'}
    review=read(final);bound={str(final):fp(final)};origins={}
    for relative,sha in anchors.items():
        p=OLD/relative;assert fp(p)['sha256']==sha
        assert review['fingerprints'][str(p)]==fp(p);bound[str(p)]=fp(p)
    cfg=read(OLD/'artifacts/configuration-before-accounts.seal.json')
    led=read(OLD/'artifacts/all-four-accounts-before-scoring.seal.json')
    wanted={**cfg['prepared_references'],**led['ledgers']}
    for p in (PRIOR/'artifacts/annual_units_hold-25bps-ledger.csv',PRIOR/'artifacts/annual_units_hold-50bps-ledger.csv',D.parent/'annual-restart2020-readiness-20261018/protocol-draft.json'):
        wanted[str(p)]=cfg['inputs'][str(p)]
    wanted[str(OLD/'restart_adapter.py')]=cfg['sources'][str(OLD/'restart_adapter.py')]
    for p,identity in wanted.items():
        assert fp(p)==identity,'SOURCE_IDENTITY:'+p
        assert review['fingerprints'][p]==identity
        bound[p]=identity;origins[p]=str(OLD/('artifacts/all-four-accounts-before-scoring.seal.json' if p in led['ledgers'] else 'artifacts/configuration-before-accounts.seal.json'))
    refs=[]
    with (OLD/'artifacts/reference-inputs.csv').open(newline='') as f:
        refs=[{k:r[k] for k in KEYS} for r in csv.DictReader(f)]
    assert len(refs)==2192
    for bps in (25,50):
        with (PRIOR/f'artifacts/annual_units_hold-{bps}bps-ledger.csv').open(newline='') as f:
            direct=[{k:r[k] for k in KEYS} for r in csv.DictReader(f) if '2020-01-01'<=r['date']<='2025-12-31']
        assert direct==refs,'WHITE_LIST_REFERENCE_MISMATCH'
    for i,r in enumerate(refs):
        d=date(2020,1,1)+timedelta(days=i)
        assert r['date']==d.isoformat() and r['decision_UTC']==d.isoformat()+'T00:10:00Z'
        assert r['feature_cutoff']==(d-timedelta(days=2)).isoformat()
        assert r['annual_generation_date']==str(d.year)+'-01-01'
        for k in ('P','reference_volume','annual_f_y'):assert math.isfinite(float(r[k]))
        assert float(r['P'])>0 and float(r['reference_volume'])>=0 and 0<=float(r['annual_f_y'])<=1
    assert refs[-1]['date']=='2025-12-31' and float(refs[0]['annual_f_y'])==K
    assert len([r for r in refs if r['date'].endswith('-01-01')])==6
    return refs,bound,origins

def prepare():
    t=time.monotonic();refs,bound,origins=checked_sources();fx=fixtures();fx['decision_fixtures']=decision_fixtures()
    refpath=A/'reference-whitelist.csv'
    assert refpath.exists()
    with refpath.open(newline='') as f:assert list(csv.DictReader(f))==refs
    save(A/'synthetic-fixtures-v2.json',fx)
    save(D/'execution/preparation-receipt-v2.json',dict(UTC=utc(),inputs=bound,source_seal_for_input=origins,adapter_identity=fp(__file__),fields=list(KEYS),no_AB_account_state_copied_to_C=True,actual_model_effort_speed='UNKNOWN',temporary_files=[],generated_files_purpose={'reference-whitelist.csv':'sealed market reference fields only, no C state','synthetic-fixtures.json':'nonmarket technical evidence','adapter.py':'single-use C implementation'},elapsed_seconds=time.monotonic()-t))
    save(A/'preflight-v2.json',dict(UTC=utc(),status='PREPARED_WAIT_FORMAL_GATE',points=len(refs),intervals=len(refs)-1,first=refs[0]['decision_UTC'],last=refs[-1]['decision_UTC'],fixed_k=K,source_fields=list(KEYS),prepared_reference={str(refpath):fp(refpath)},adapter={str(Path(__file__).resolve()):fp(__file__)},inputs=bound,synthetic=fp(A/'synthetic-fixtures-v2.json'),protocol={str(D/'root/protocol.json'):fp(D/'root/protocol.json')},supervisor={str(D/'execution/supervise.py'):fp(D/'execution/supervise.py')},real_market_C_accounts_created=0))
    print('PREPARED_WAIT_FORMAL_GATE',flush=True)

def load_ledger(path):
    numeric=('P','reference_volume','cost_bps','frozen_target','pretrade_equity','posttrade_equity','pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','driftedweight','actualweight','trade_BTC','reference_trade_USD','cost_USD','net_interval_return')
    boolean=('pending_before','pending_after','newyear_replaced_pending','attempt','entered_after_row','terminal','allocation_completed','zero_volume_no_fill')
    with Path(path).open(newline='') as f:rows=list(csv.DictReader(f))
    for r in rows:
        for k in numeric:r[k]=float(r[k]) if r[k]!='' else None
        for k in boolean:r[k]={'True':True,'False':False}[r[k]]
    return rows

def comparison(a,c):
    dw=a['end_equity_USD']-c['end_equity_USD'];dd=a['maximum_drawdown']-c['maximum_drawdown']
    wt=max(1e-6,1e-10*max(abs(a['end_equity_USD']),abs(c['end_equity_USD']),1));dt=1e-10
    return dict(wealth_A_minus_C=dw,DD_A_minus_C=dd,USD_tolerance=wt,DD_tolerance=dt,
        A_wealth_strictly_higher=dw>wt,A_DD_not_worse=dd<=dt,
        C_wealth_not_lower=dw<=wt,C_DD_not_worse=dd>=-dt,
        C_wealth_strictly_higher=dw<-wt,C_DD_strictly_lower=dd>dt,
        wealth_tied=abs(dw)<=wt,DD_tied=abs(dd)<=dt,
        Sharpe_A_minus_C=a['Sharpe']-c['Sharpe'] if a.get('Sharpe') is not None and c.get('Sharpe') is not None else None,
        volatility_A_minus_C=a.get('annualized_volatility',0)-c.get('annualized_volatility',0),
        exposure_A_minus_C=a.get('average_exposure',0)-c.get('average_exposure',0))
def combined_classification(flags):
    fs=list(flags.values())
    if all(f['wealth_tied'] and f['DD_tied'] for f in fs):return 'TIE'
    if all(f['A_wealth_strictly_higher'] and f['A_DD_not_worse'] for f in fs):return 'A_DESCRIPTIVELY_DOMINATES_C'
    if all(f['C_wealth_not_lower'] and f['C_DD_not_worse'] for f in fs) and any(f['C_wealth_strictly_higher'] or f['C_DD_strictly_lower'] for f in fs):return 'C_DESCRIPTIVELY_DOMINATES_A'
    return 'MIXED'
def decision_fixtures():
    def one(w,d):return {'end_equity_USD':w,'maximum_drawdown':d}
    tie=comparison(one(5000,.5),one(5000+1e-7,.5+1e-11))
    ad=comparison(one(5100,.4),one(5000,.5))
    cd=comparison(one(5000,.5),one(5000,.4))
    cm=comparison(one(5000,.5),one(5100,.4))
    mixed=comparison(one(5100,.6),one(5000,.5))
    assert combined_classification({'25':tie,'50':tie})=='TIE'
    assert combined_classification({'25':ad,'50':ad})=='A_DESCRIPTIVELY_DOMINATES_C'
    assert combined_classification({'25':cd,'50':tie})=='C_DESCRIPTIVELY_DOMINATES_A'
    assert combined_classification({'25':cm,'50':cm})=='C_DESCRIPTIVELY_DOMINATES_A'
    assert combined_classification({'25':ad,'50':tie})=='MIXED'
    assert combined_classification({'25':mixed,'50':mixed})=='MIXED'
    assert combined_classification({'25':ad,'50':cm})=='MIXED'
    return {'status':'PASS_SYNTHETIC_DECISION','cases':['within_tolerance_tie','A_both_wealth_strict_DD_not_worse','C_equal_wealth_lower_DD_one_cost','C_both_dominant','A_one_cost_tied_is_mixed','wealth_risk_tradeoff_mixed','cost_conflict_mixed']}

def run(gate_path):
    global FORMAL_START
    FORMAL_START=time.monotonic()
    gate_path=Path(gate_path);g=read(gate_path);pre=read(A/'preflight-v2.json');protocol=D/'root/protocol.json'
    assert g['allow_formal_C'] is True
    assert g['preflight_identity']==fp(A/'preflight-v2.json')
    assert g['adapter_identity']==fp(__file__)
    assert g['protocol_identity']==fp(protocol)
    for group in ('inputs','adapter','prepared_reference','protocol','supervisor'):
        for p,ident in pre[group].items():assert fp(p)==ident,'PREFLIGHT_CHANGED:'+p
    assert fp(A/'synthetic-fixtures-v2.json')==pre['synthetic']
    assert datetime.now(timezone.utc)<datetime.fromisoformat(g['work_deadline_UTC'])
    lock=D/'execution/formal-C-started.lock'
    save(lock,dict(UTC=utc(),PID=os.getpid(),gate={str(gate_path):fp(gate_path)}))
    save(A/'configuration-before-C.seal.json',dict(UTC=utc(),protocol={str(protocol):fp(protocol)},gate={str(gate_path):fp(gate_path)},preflight=fp(A/'preflight-v2.json'),adapter=fp(__file__),inputs=pre['inputs'],prepared_reference=pre['prepared_reference']))
    with (A/'reference-whitelist.csv').open(newline='') as f:points=[{k:float(v) if k in ('P','reference_volume','annual_f_y') else v for k,v in r.items()} for r in csv.DictReader(f)]
    cfiles={}
    for cost in (25,50):
        rows=ledger_C(points,cost)
        assert len(rows)==2192 and rows[-1]['posttrade_units']==0,'C_TERMINAL_INVALID'
        p=A/f'C-fixedmix2020-{cost}bps-ledger.csv'
        with p.open('x',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
        cfiles[str(p)]=fp(p)
    abfiles={p:v for p,v in pre['inputs'].items() if Path(p).name.startswith(('A-fresh2020-','B-fresh2020-'))}
    assert len(abfiles)==4
    save(A/'all-six-accounts-before-scoring.seal.json',dict(UTC=utc(),existing_AB=abfiles,new_C=cfiles,scoring_started=False))
    result={};classes={};logs={};same_initial={}
    for cost in (25,50):
        result[str(cost)]={};accounts={}
        for method in ('A','B','C'):
            p=A/f'C-fixedmix2020-{cost}bps-ledger.csv' if method=='C' else OLD/f'artifacts/{method}-fresh2020-{cost}bps-ledger.csv'
            rr=load_ledger(p);accounts[method]=rr
            assert len(rr)==2192 and rr[-1]['posttrade_units']==0
            result[str(cost)][method]=metrics(rr)
        for method in ('A','B'):
            for k in ('pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','cost_USD'):
                assert accounts['C'][0][k]==accounts[method][0][k],'INITIAL_COMMON_ENTRY'
            for i,p in enumerate(points):
                if p['date']>='2021-01-01':break
                for k in ('pretrade_equity','posttrade_equity','posttrade_cash','posttrade_units'):
                    assert accounts['C'][i][k]==accounts[method][i][k],'COMMON_2020_PATH'
        same_initial[str(cost)]=True
        a=result[str(cost)]['A']['overall'];c=result[str(cost)]['C']['overall']
        logs[str(cost)]=math.log(a['end_equity_USD']/c['end_equity_USD']);classes[str(cost)]=comparison(a,c)
    combined=combined_classification(classes)
    path=A/'evaluation-results.json'
    save(path,dict(UTC=utc(),status='VALID_DESCRIPTIVE_COMPARISON',primary_25bps_log_WA_over_WC=logs['25'],stress_50bps_log_WA_over_WC=logs['50'],per_cost_comparison_flags=classes,combined_descriptive_classification=combined,metrics=result,common_entry_and_full_2020_equality=same_initial,old_AB_gate_unchanged=True,new_independent_market_samples=0,fresh_OOS=False,actual_trades=0,paid_resources=0,execution_fill_capacity_alpha_and_wealth='NOT_ESTABLISHED',no_Sharpe_or_risk_ratio_hurdles=True))
    for p,v in pre['inputs'].items():assert fp(p)==v,'SOURCE_CHANGED_AFTER_RUN'
    deadline()
    save(A/'final-result.seal.json',dict(UTC=utc(),result={str(path):fp(path)},ledger_seal=fp(A/'all-six-accounts-before-scoring.seal.json'),configuration_seal=fp(A/'configuration-before-C.seal.json'),unchanged_inputs=pre['inputs'],lock=fp(lock),formal_units=1,new_C_paths=2))
    print(json.dumps(dict(status='VALID_DESCRIPTIVE_COMPARISON',formal_units=1,new_C_paths=2)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('prepare','run'));p.add_argument('--gate');args=p.parse_args()
    if args.stage=='prepare':prepare()
    else:
        assert args.gate
        run(args.gate)
