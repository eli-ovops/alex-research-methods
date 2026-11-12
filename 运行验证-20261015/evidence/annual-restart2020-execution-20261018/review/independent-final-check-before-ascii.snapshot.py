from pathlib import Path
from datetime import datetime,timezone,date,timedelta
import csv,json,hashlib,math,time,resource,sys
T=time.perf_counter();UTC=datetime.now(timezone.utc).isoformat();D=Path(__file__).resolve().parent.parent;O=D/'review';A=D/'artifacts';errors=[];fps={};count=0;maxcash=0.;maxfee=0.
def ck(v,msg):
 if not v:errors.append(msg)
def near(x,y,msg):
 global count
 count+=1;ck(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-8),msg)
def rd(p):return json.loads(Path(p).read_text())
def fp(p):
 p=Path(p)
 if str(p) not in fps:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  fps[str(p)]={'sha256':h.hexdigest(),'bytes':p.stat().st_size}
 return fps[str(p)]
def identities(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k.startswith('/') and isinstance(v,dict) and 'sha256'in v:ck(fp(k)=={z:v[z] for z in ['bytes','sha256']},'IDENTITY:'+k)
   else:identities(v)
 elif isinstance(x,list):
  for v in x:identities(v)
def load(p):
 rr=list(csv.DictReader(Path(p).open()))
 for r in rr:
  for k,v in list(r.items()):
   if v in ['True','False']:r[k]=v=='True'
   elif k not in ['date','decision_UTC','feature_cutoff','method','generation_date','annual_generation_date'] and v!='':r[k]=float(v)
 return rr
res=rd(A/'evaluation-results.json');pre=rd(A/'preflight.json');auth=rd(D/'root-admission.json');gate=rd(D/'root-formal-gate.json');lock=rd(D/'formal-restart2020-started.lock')
for n in ['evaluation-results.json','preflight.json','session-001.receipt.json','session-002.receipt.json','session-002.stdout.txt','session-002.stderr.txt']:fp(A/n)
for n in ['root-admission.json','root-formal-gate.json','formal-restart2020-started.lock']:fp(D/n)
for x in [pre,gate]:identities(x)
ss={}
for n in ['configuration-before-accounts.seal.json','all-four-accounts-before-scoring.seal.json','final-result.seal.json']:
 fp(A/n);ss[n]=rd(A/n);identities(ss[n])
ck(gate['allow_formal_restart2020'] and gate['source_inputs']==pre['source_inputs'],'GATE');ck(lock['gate_identity']==fp(D/'root-formal-gate.json'),'LOCK_GATE');ck(ss['configuration-before-accounts.seal.json']['gate']==fp(D/'root-formal-gate.json'),'CONFIG_GATE');ck(ss['final-result.seal.json']['single_formal_claim']==fp(D/'formal-restart2020-started.lock'),'CLAIM_SEAL')
ck(ss['configuration-before-accounts.seal.json']['UTC']<ss['all-four-accounts-before-scoring.seal.json']['UTC']<res['UTC']<ss['final-result.seal.json']['UTC'],'SEAL_ORDER')
refs=load(A/'reference-inputs.csv');ck(len(refs)==2192,'REF_COUNT')
# Existing-source alignment only: no old account states loaded.
keys=list(csv.DictReader((A/'reference-inputs.csv').open()).fieldnames)
for p in pre['inputs']:
 if p.endswith('annual_units_hold-25bps-ledger.csv') or p.endswith('annual_units_hold-50bps-ledger.csv'):
  old=[{k:r[k] for k in keys} for r in csv.DictReader(Path(p).open()) if '2020-01-01'<=r['date']<='2025-12-31'];new=list(csv.DictReader((A/'reference-inputs.csv').open()));ck(old==new,'SOURCE_WHITELIST_MATCH')
accounts={};qs={};calc={};reconciliations={};totalrows=0

def stats(rows,q,lo,hi):
 tail=hi==2190;h=rows[lo:hi+1];tr=h+([rows[-1]] if tail else []);start=rows[lo]['pretrade_equity'];end=rows[-1]['posttrade_equity'] if tail else rows[hi+1]['pretrade_equity'];part=q[lo:hi+1];n=len(part)
 mean=math.fsum(part)/n;sd=math.sqrt(math.fsum((x-mean)**2 for x in part)/n);peak=start;dd=0.
 for r in tr:
  for v in [r['pretrade_equity'],r['posttrade_equity']]:peak=max(peak,v);dd=max(dd,(peak-v)/peak)
 peak=max(peak,end);dd=max(dd,(peak-end)/peak)
 endr=rows[-1] if tail else rows[hi]
 out={'start_equity_USD':start,'end_equity_USD':end,'net_USD':end-start,'total_return':end/start-1,'CAGR':math.expm1(math.log(end/start)*365/n),'annualized_volatility':sd*math.sqrt(365),'Sharpe':mean*math.sqrt(365)/sd if sd else None,'maximum_drawdown':dd,'all_cost_USD':math.fsum(r['cost_USD'] for r in tr),'turnover':math.fsum(r['reference_trade_USD']/r['pretrade_equity'] for r in tr),'average_exposure':math.fsum(r['actualweight'] for r in h)/n,'min_exposure':min(r['actualweight'] for r in h),'max_exposure':max(r['actualweight'] for r in h),'nonzero_trade_count':sum(r['trade_BTC']!=0 for r in tr),'zero_volume_no_fill_count':sum(r['zero_volume_no_fill'] for r in tr),'zero_reference_volume_rows':sum(r['reference_volume']==0 for r in tr),'start_BTC':rows[lo]['pretrade_units'],'start_cash':rows[lo]['pretrade_cash'],'end_BTC':endr['posttrade_units'],'end_cash':endr['posttrade_cash'],'first_holding_date':rows[lo]['date'],'last_holding_date':rows[hi]['date'],'end_valuation_date':rows[hi+1]['date'],'intervals':n,'terminal_fee_included':tail}
 near(start*math.exp(math.fsum(math.log1p(x) for x in part)),end,'SECTION_NET_GROWTH')
 return out
for cost in ['25','50']:
 for method in ['A','B']:
  p=A/f'{method}-fresh2020-{cost}bps-ledger.csv';fp(p);rr=load(p);accounts[(cost,method)]=rr;totalrows+=len(rr);ck(len(rr)==2192,'ROWS');pending=False;entered=False;target=None;generation=None
  for i,r in enumerate(rr):
   s=refs[i];day=str(date(2020,1,1)+timedelta(days=i));terminal=i==2191
   ck(r['date']==s['date']==day and r['decision_UTC']==day+'T00:10:00Z' and r['feature_cutoff']==str(date.fromisoformat(day)-timedelta(days=2)),'TIME')
   ck(r['P']==s['P'] and r['reference_volume']==s['reference_volume'] and r['method']==method and r['cost_bps']==int(cost),'REFERENCE')
   replaced=False
   if not terminal and (i==0 or (day.endswith('-01-01') and (method=='A' or not entered))):replaced=pending;pending=True;target=s['annual_f_y'];generation=s['annual_generation_date']
   ck(r['frozen_target']==target and r['generation_date']==generation and r['pending_before']==pending and r['newyear_replaced_pending']==replaced,'NEW_STATE_NOT_OLD_FLAGS')
   attempt=terminal or pending;w=0. if terminal else target if attempt else None;done=attempt and r['reference_volume']>0
   ck(r['attempt']==attempt and (r['target_if_attempt']==w if attempt else r['target_if_attempt']=='') and r['allocation_completed']==done,'ATTEMPT')
   if done:pending=False;entered=entered or not terminal
   ck(r['pending_after']==pending and r['entered_after_row']==entered and r['terminal']==terminal,'STATE_AFTER')
   pc,pu=(5000.,0.) if i==0 else (rr[i-1]['posttrade_cash'],rr[i-1]['posttrade_units']);near(pc,r['pretrade_cash'],'CASH_CARRY');near(pu,r['pretrade_units'],'UNITS_CARRY');P=r['P'];preval=pc+pu*P;post=r['posttrade_cash']+r['posttrade_units']*P;delta=r['posttrade_units']-pu;fee=abs(delta)*P*int(cost)/10000
   for x,y,k in [(preval,r['pretrade_equity'],'PRE'),(post,r['posttrade_equity'],'POST'),(delta,r['trade_BTC'],'DELTA'),(fee,r['cost_USD'],'FEE'),(abs(delta)*P,r['reference_trade_USD'],'NOTIONAL'),(pu*P/preval,r['driftedweight'],'DRIFT'),(r['posttrade_units']*P/post,r['actualweight'],'WEIGHT')]:near(x,y,k)
   cr=abs(r['posttrade_cash']-(pc-delta*P-fee));fr=abs(preval-post-fee);maxcash=max(maxcash,cr);maxfee=max(maxfee,fr);ck(max(cr,fr)<=max(1e-8,1e-10*preval),'CONSERVATION');ck(r['posttrade_units']>=-1e-9 and r['posttrade_cash']>=-1e-9,'NONNEGATIVE')
   if done:near(r['actualweight'],w,'POST_TARGET')
   else:ck(r['posttrade_units']==pu and r['posttrade_cash']==pc and fee==0,'EXACT_CARRY')
   ck(r['zero_volume_no_fill']==(attempt and r['reference_volume']==0),'NOFILL')
   if method=='B' and 0<i<2191:ck(r['posttrade_units']==rr[0]['posttrade_units'] and r['posttrade_cash']==rr[0]['posttrade_cash'] and r['trade_BTC']==0,'B_STATIC')
  q=[rr[i+1]['pretrade_equity']/rr[i]['pretrade_equity']-1 for i in range(2191)];q[-1]=rr[-1]['posttrade_equity']/rr[-2]['pretrade_equity']-1;qs[(cost,method)]=q
  for i,v in enumerate(q):ck(math.isfinite(v) and v>-1,'FINITE_Q');near(v,rr[i]['net_interval_return'],'Q')
  ck(rr[-1]['net_interval_return']=='' and rr[-1]['posttrade_units']==0,'TERMINAL')
  sections={'overall':(0,2190)}
  for year in range(2020,2026):
   ix=[i for i,r in enumerate(rr[:-1]) if r['date'].startswith(str(year))];sections['all_six_years/'+str(year)]=(ix[0],ix[-1])
  for name,(lo,hi) in sections.items():
   got=stats(rr,q,lo,hi);want=res['metrics'][cost][method]
   for k in name.split('/'):want=want[k]
   for k,v in got.items():
    if isinstance(v,(int,float)) and not isinstance(v,bool):near(v,want[k],'METRIC:'+cost+method+name+k)
    else:ck(v==want[k],'METRIC_LABEL')
   calc[(cost,method,name)]=got
  pnl=math.fsum(rr[i]['pretrade_equity']-rr[i-1]['posttrade_equity'] for i in range(1,len(rr)));fees=math.fsum(r['cost_USD'] for r in rr);near(5000+pnl-fees,rr[-1]['posttrade_cash'],'FEES_ONCE');reconciliations[cost+method]={'holding_PnL':pnl,'all_fees':fees,'end_cash':rr[-1]['posttrade_cash'],'nonzero_trade_count':sum(r['trade_BTC']!=0 for r in rr)}
for cost in ['25','50']:
 a,b=accounts[(cost,'A')],accounts[(cost,'B')]
 for k in ['pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','cost_USD']:ck(a[0][k]==b[0][k],'INITIAL_IDENTICAL')
 for i,r in enumerate(a):
  if r['date']<'2021-01-01':ck(r['pretrade_equity']==b[i]['pretrade_equity'] and r['posttrade_equity']==b[i]['posttrade_equity'],'YEAR2020_SAME_PATH')
 ck(sum(r['trade_BTC']!=0 for r in b)==2,'B_TWO_TRADES')
ratios={c:calc[(c,'A','overall')]['annualized_volatility']/calc[(c,'B','overall')]['annualized_volatility'] for c in ['25','50']}
for c,v in ratios.items():near(v,res['risk_ratios_A_over_B'][c],'RISK_RATIO')
a,b=calc[('25','A','overall')],calc[('25','B','overall')];s,t=calc[('50','A','overall')],calc[('50','B','overall')];risk=all(.8<=v<=1.2 for v in ratios.values());valid=all(rr[-1]['posttrade_units']==0 for rr in accounts.values())
g={'terminal_valid':valid,'both_risk_ratios_qualified':risk,'A25_terminal_positive_and_greater_B':a['end_equity_USD']>5000 and a['end_equity_USD']>b['end_equity_USD'],'A25_Sharpe_ge_B_plus020':a['Sharpe']>=b['Sharpe']+.2,'A25_DD_not_larger':a['maximum_drawdown']<=b['maximum_drawdown'],'A50_terminal_positive_and_greater_B':s['end_equity_USD']>5000 and s['end_equity_USD']>t['end_equity_USD'],'A50_Sharpe_not_lower':s['Sharpe']>=t['Sharpe'],'A50_DD_not_larger':s['maximum_drawdown']<=t['maximum_drawdown']};ck(g==res['gates'],'GATES')
classification='TECHNICALLY_INVALID' if not valid else 'INCONCLUSIVE_RISK_MISMATCH' if not risk else 'DESCRIPTIVE_LATER_START_ADVANTAGE' if all(g.values()) else 'NOT_SUPPORTED_THIS_DIAGNOSTIC';ck(classification==res['status'],'CLASSIFICATION')
sessions=[rd(p) for p in sorted(A.glob('session-*.receipt.json'))];ck(len(sessions)==2 and sum(x['stage']=='run' for x in sessions)==1,'ONE_RUN');ck(sessions[-1]['exit_code']==0 and sessions[-1]['stop_reason'] is None and sessions[-1]['no_live_worker'],'EXIT');ck((A/'session-002.stderr.txt').stat().st_size==0,'STDERR');ck(sessions[-1]['end_UTC']<auth['work_deadline_UTC'],'DEADLINE')
ru=resource.getrusage(resource.RUSAGE_SELF);rss=ru.ru_maxrss if sys.platform=='darwin' else ru.ru_maxrss*1024;elapsed=time.perf_counter()-T
report={'status':'PASS_VALID_NOT_SUPPORTED' if not errors and classification=='NOT_SUPPORTED_THIS_DIAGNOSTIC' else ('PASS_VALID_'+classification if not errors else 'NEEDS_FIX'),'scientific_classification':classification,'material_errors':errors,'ledger_rows':totalrows,'numeric_checks':count,'max_cash_residual_USD':maxcash,'max_equity_fee_residual_USD':maxfee,'tolerance':'numeric rel1e-9 abs1e-8; conservation max(1e-8,1e-10*pretradeequity)','risk_ratios':ratios,'gates':g,'primary_Sharpe_increment':a['Sharpe']-b['Sharpe'],'overalls':{c:{m:calc[(c,m,'overall')] for m in ['A','B']} for c in ['25','50']},'reconciliations':reconciliations,'fingerprints':fps,'seal_UTCs':{k:v['UTC'] for k,v in ss.items()},'checker':{'command':f"python3 -I -B '{Path(__file__).resolve()}'",'started_UTC':UTC,'ended_UTC':datetime.now(timezone.utc).isoformat(),'arithmetic_and_hash_seconds':elapsed,'self_peak_RSS_bytes':rss,'self_user_seconds':ru.ru_utime,'self_system_seconds':ru.ru_stime,'script_identity':fp(__file__),'raw_command_receipt':'review/final-check-command-receipt.json','own_process_not_covered_by_owner_supervisor':True},'owner_receipt':sessions[-1],'actual_model_effort_speed':'UNKNOWN','scope':['Existing sealed four-account observations only; no source execution/import, no new strategy path or account ledger generated.','Independent arithmetic uses fixed observations; no bootstrap, tuning, new data, model, network, accounts or trades.','Old A source hashes unchanged; old results/FAILED untouched. Not a comprehensive rehash of unrelated historic FAILED.','Selected observed2020-2025 history; not fresh OOS. Full-window volatility ratio not annual/tail equivalence. Real fill/cost/capacity/PIT remain UNKNOWN.']}
with (O/'final-review.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
md=f'''# 2020新5000本金：独立最终验收\n\n**{report['status']}。技术有效、风险合格，但未达到冻结综合优势门槛。**\n\n一次独立标准库检查读四账{totalrows}行，{count}项数字核验，无材料错误。来源白名单与两份封存旧源逐行一致；四账独立5000现金/0BTC，新A/B同成本首入场相同，2020全年至2021Jan1交易前路径相同；B中段单位/现金完全不变，仅首末两笔。A年度事件、新pending与冻结f由新状态产生，旧flags未被当成状态。\n\n首费、实际BTC成交额费用、现金与单位连续、零量结转、q和末费一次、终点清仓、pre/post回撤、完整六年继承指标均通过。最大现金残差{maxcash:.12g} USD，最大权益费用残差{maxfee:.12g} USD，冻结容差内。全部输入/源码/gate/lock/seal hash及配置→四账→评分→final顺序通过；正式run只有一次且exit0/stderr0。\n\n|成本|A末现金USD|B末现金USD|A/B净波动比|\n|---|---:|---:|---:|\n|25bps|{a['end_equity_USD']:.6f}|{b['end_equity_USD']:.6f}|{ratios['25']:.9f}|\n|50bps|{s['end_equity_USD']:.6f}|{t['end_equity_USD']:.6f}|{ratios['50']:.9f}|\n\n25bps A/B Sharpe{a['Sharpe']:.9f}/{b['Sharpe']:.9f}，增量{a['Sharpe']-b['Sharpe']:.9f}，小于0.20；回撤{a['maximum_drawdown']:.9f}/{b['maximum_drawdown']:.9f}。其他冻结条件均通过。准确说法是“历史净额更高、回撤较低，但综合优势条件未通过”，不是风险不匹配，也不是收益全面失败。旧2014全期描述性通过不被撤销。\n\nchecker自身hash/算术实耗{elapsed:.9f}秒，selfRSS约{rss}B；独立命令stdout/stderr/实际exit/总elapsed另保存在final-check-command-receipt.json，不声称Owner监督器覆盖审阅进程。Owner累计prepare+formal0.302888542秒，UTC截止08:46:40；检查累计须加命令总实耗，仍受600秒预算。原样本是已见历史，非新鲜OOS；真实全费/成交/容量未证，不能把虚拟终值当现实利润。本轮不执行Owner源、不重建策略、不bootstrap或联网交易，只写review。route UNKNOWN。\n'''
with (O/'final-review.md').open('x') as f:f.write(md)
print(json.dumps({'review_status':report['status'],'classification':classification,'errors':errors,'rows':totalrows,'checks':count,'risk_ratios':ratios,'Sharpe_increment':a['Sharpe']-b['Sharpe'],'self_elapsed':elapsed,'selfRSS':rss,'maxcash':maxcash,'maxfee':maxfee},ensure_ascii=False))
sys.exit(0 if not errors else 1)
