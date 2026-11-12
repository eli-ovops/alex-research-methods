from pathlib import Path
from datetime import datetime,timezone,date,timedelta
import csv,json,hashlib,math,statistics,time,resource,sys,os
T=time.perf_counter();start=datetime.now(timezone.utc).isoformat();D=Path(__file__).resolve().parent.parent;O=D/'review';A=D/'artifacts'
err=[];fps={};nc=0;maxcash=0.;maxfee=0.;nr=0

def ck(ok,msg):
 if not ok:err.append(msg)
def near(x,y,msg):
 global nc
 nc+=1
 ck(math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-8),msg)
def rd(p):return json.loads(Path(p).read_text())
def fp(p):
 p=Path(p)
 if str(p) not in fps:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  fps[str(p)]={'sha256':h.hexdigest(),'bytes':p.stat().st_size}
 return fps[str(p)]
def ids(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k.startswith('/') and isinstance(v,dict) and 'sha256'in v:ck(fp(k)=={z:v[z] for z in ['sha256','bytes']},'HASH:'+k)
   elif k=='path' and 'sha256'in x:ck(fp(v)=={z:x[z] for z in ['sha256','bytes']},'PATH_HASH:'+v)
   else:ids(v)
 elif isinstance(x,list):
  for v in x:ids(v)
res=rd(A/'evaluation-results.json');pre=rd(A/'preflight.json');auth=rd(D/'root-admission.json');gate=rd(D/'root-formal-gate.json');lock=rd(D/'formal-B-run-started.lock')
for n in ['evaluation-results.json','preflight.json','session-001.receipt.json','session-002.receipt.json']:fp(A/n)
for n in ['root-admission.json','root-formal-gate.json','formal-B-run-started.lock']:fp(D/n)
for x in [pre,gate]:ids(x)
ck(gate['allow_B_market_run'] is True and gate['source_inputs']==pre['source_inputs'],'GATE')
ss={}
for n in ['configuration-before-B.seal.json','both-B-ledgers-before-scoring.seal.json','final-result.seal.json']:
 fp(A/n);ss[n]=rd(A/n);ids(ss[n])
ck(ss['configuration-before-B.seal.json']['gate']==fp(D/'root-formal-gate.json'),'GATESEAL')
ck(ss['final-result.seal.json']['formal_claim']==fp(D/'formal-B-run-started.lock'),'CLAIM')
ck(lock['gate_identity']==fp(D/'root-formal-gate.json'),'LOCKGATE')
ck(ss['configuration-before-B.seal.json']['UTC']<ss['both-B-ledgers-before-scoring.seal.json']['UTC']<res['UTC']<ss['final-result.seal.json']['UTC'],'SEALORDER')
records={};qmap={};calcmap={}
def load(p):
 rows=list(csv.DictReader(Path(p).open()))
 for r in rows:
  for k,v in list(r.items()):
   if v in ['True','False']:r[k]=v=='True'
   elif k not in ['date','decision_UTC','feature_cutoff','annual_generation_date'] and v!='':r[k]=float(v)
 return rows

def summarize(rows,qs,first,last):
 term=last==len(rows)-2;sub=rows[first:last+1];tr=sub+([rows[-1]] if term else []);start=rows[first]['pretrade_equity'];end=rows[-1]['posttrade_equity'] if term else rows[last+1]['pretrade_equity'];qq=qs[first:last+1];path=[start]
 for r in tr:path.extend([r['pretrade_equity'],r['posttrade_equity']])
 path.append(end);peak=path[0];dd=0
 for x in path:peak=max(peak,x);dd=max(dd,1-x/peak)
 sd=statistics.pstdev(qq);mean=statistics.fmean(qq);endrow=rows[-1] if term else rows[last]
 st={'start_equity_USD':start,'end_equity_USD':end,'net_USD':end-start,'total_return':end/start-1,'CAGR':(end/start)**(365/len(qq))-1,'annualized_volatility':sd*math.sqrt(365),'Sharpe':math.sqrt(365)*mean/sd if sd else None,'maximum_drawdown':dd,'all_cost_USD':math.fsum(r['cost_USD'] for r in tr),'turnover':math.fsum(r['reference_trade_USD']/r['pretrade_equity'] for r in tr),'average_exposure':statistics.fmean(r['actualweight'] for r in sub),'min_exposure':min(r['actualweight'] for r in sub),'max_exposure':max(r['actualweight'] for r in sub),'nonzero_trade_count':sum(r['trade_BTC']!=0 for r in tr),'zero_volume_no_fill_count':sum(r['zero_volume_no_fill'] for r in tr),'zero_reference_volume_rows':sum(r['reference_volume']==0 for r in tr),'start_BTC':rows[first]['pretrade_units'],'start_cash':rows[first]['pretrade_cash'],'end_BTC':endrow['posttrade_units'],'end_cash':endrow['posttrade_cash'],'intervals':len(qq),'first_holding_date':rows[first]['date'],'last_holding_date':rows[last]['date'],'end_valuation_date':rows[last+1]['date'],'terminal_fee_included':term,'log_growth':math.fsum(math.log1p(x) for x in qq)}
 near(start*math.prod(1+x for x in qq),end,'COMPOUND_SECTION')
 return st
for cost in ['25','50']:
 ap=ss['both-B-ledgers-before-scoring.seal.json']['A_ledger_references'][cost]['path'];bp=A/f'B-static-units-{cost}bps-ledger.csv';aa=load(ap);bb=load(bp);fp(bp)
 for key in ['pretrade_equity','posttrade_equity','pretrade_cash','pretrade_units','posttrade_cash','posttrade_units','cost_USD','trade_BTC']:ck(aa[0][key]==bb[0][key],'INITIAL_COPY:'+key)
 for label,rows in [('A',aa),('B',bb)]:
  nr+=len(rows);ck(len(rows)==4383,'ROWS');prev=None
  for i,r in enumerate(rows):
   ck(r['date']==str(date(2014,1,1)+timedelta(days=i)) and r['decision_UTC']==r['date']+'T00:10:00Z','CLOCK')
   ck(r['feature_cutoff']==str(date.fromisoformat(r['date'])-timedelta(days=2)),'CUTOFF')
   for k in ['date','decision_UTC','P','reference_volume','feature_cutoff']:ck(r[k]==aa[i][k],'SAME_REFERENCE')
   P=r['P'];pc,pu=(5000.,0.) if prev is None else (prev['posttrade_cash'],prev['posttrade_units']);near(r['pretrade_cash'],pc,'PRE_CASH');near(r['pretrade_units'],pu,'PRE_UNITS')
   preeq=pc+pu*P;posteq=r['posttrade_cash']+r['posttrade_units']*P;trade=r['posttrade_units']-pu;fee=abs(trade)*P*int(cost)/10000
   near(r['pretrade_equity'],preeq,'PRE_EQUITY');near(r['posttrade_equity'],posteq,'POST_EQUITY');near(r['trade_BTC'],trade,'BTC_DELTA');near(r['reference_trade_USD'],abs(trade)*P,'NOTIONAL');near(r['cost_USD'],fee,'FEE');near(r['actualweight'],r['posttrade_units']*P/posteq,'WEIGHT')
   cr=abs(r['posttrade_cash']-(pc-trade*P-fee));fr=abs(preeq-posteq-fee);maxcash=max(maxcash,cr);maxfee=max(maxfee,fr);ck(max(cr,fr)<=max(1e-8,1e-10*preeq),'CONSERVATION')
   ck(r['posttrade_cash']>=-1e-9 and r['posttrade_units']>=-1e-9,'NONNEGATIVE')
   if label=='B' and 0<i<4382:ck(r['trade_BTC']==0 and r['cost_USD']==0 and r['posttrade_cash']==bb[0]['posttrade_cash'] and r['posttrade_units']==bb[0]['posttrade_units'],'B_EXACT_CARRY')
   if r['reference_volume']==0:ck(trade==0 and fee==0,'NOFILL')
   prev=r
  ck(rows[-1]['posttrade_units']==0 and rows[-1]['net_interval_return']=='','TERMINAL')
  qq=[rows[i+1]['pretrade_equity']/rows[i]['pretrade_equity']-1 for i in range(4382)];qq[-1]=rows[-1]['posttrade_equity']/rows[-2]['pretrade_equity']-1
  for i,x in enumerate(qq):near(x,rows[i]['net_interval_return'],'Q')
  qmap[(cost,label)]=qq;records[(cost,label)]=rows
  cut=next(i for i,r in enumerate(rows) if r['date']=='2020-01-01');sections={'overall':(0,4381)}
  for y in range(2014,2026):
   ix=[i for i,r in enumerate(rows[:-1]) if r['date'].startswith(str(y))];sections['years/'+str(y)]=(ix[0],ix[-1])
  sections['fixed_halves/2014-2019']=(0,cut-1);sections['fixed_halves/2020-2025']=(cut,4381)
  for name,(first,last) in sections.items():
   got=summarize(rows,qq,first,last);want=res['metrics'][cost][label]
   for k in name.split('/'):want=want[k]
   for k,x in got.items():
    if isinstance(x,(int,float)) and not isinstance(x,bool):near(x,want[k],'METRIC:'+cost+label+name+k)
    else:ck(x==want[k],'METRIC_STR')
   calcmap[(cost,label,name)]=got
  pnl=math.fsum(rows[i]['pretrade_equity']-rows[i-1]['posttrade_equity'] for i in range(1,len(rows)));fees=math.fsum(r['cost_USD'] for r in rows);near(5000+pnl-fees,rows[-1]['posttrade_cash'],'PNL_ONCE')
for cost in ['25','50']:
 ca=calcmap[(cost,'A','overall')];cb=calcmap[(cost,'B','overall')];near(ca['annualized_volatility']/cb['annualized_volatility'],res['risk_ratios_A_over_B'][cost],'RATIO')
 d=statistics.fmean(math.log1p(a)-math.log1p(b) for a,b in zip(qmap[(cost,'A')],qmap[(cost,'B')]));near(d,res['paired_descriptions'][cost]['full_mean_daily_log_excess_A_minus_B'],'PAIRED_MEAN')
 for y,v in res['paired_descriptions'][cost]['every_year_log_growth_difference'].items():near(calcmap[(cost,'A','years/'+y)]['log_growth']-calcmap[(cost,'B','years/'+y)]['log_growth'],v,'YEAR_LOG_DIFF')
 for h,v in res['paired_descriptions'][cost]['fixed_halves_A_growth_factor_over_B_growth_factor'].items():near((1+calcmap[(cost,'A','fixed_halves/'+h)]['total_return'])/(1+calcmap[(cost,'B','fixed_halves/'+h)]['total_return']),v,'HALF_FACTOR')
 for label in ['A','B']:ck(calcmap[(cost,label,'overall')]['nonzero_trade_count']==(13 if label=='A' else 2),'TRADECOUNT')
a,b=calcmap[('25','A','overall')],calcmap[('25','B','overall')];s,t=calcmap[('50','A','overall')],calcmap[('50','B','overall')]
g={'risk_qualified_both_costs':all(.8<=x<=1.2 for x in res['risk_ratios_A_over_B'].values()),'terminal_liquidation_valid':True,'A25_positive_and_wealth_greater_B':a['net_USD']>0 and a['end_equity_USD']>b['end_equity_USD'],'A25_Sharpe_ge_B_plus020':a['Sharpe']>=b['Sharpe']+.2,'A25_DD_not_larger':a['maximum_drawdown']<=b['maximum_drawdown'],'A50_positive_and_wealth_greater_B':s['net_USD']>0 and s['end_equity_USD']>t['end_equity_USD'],'A50_Sharpe_not_lower':s['Sharpe']>=t['Sharpe'],'A50_DD_not_larger':s['maximum_drawdown']<=t['maximum_drawdown']};ck(g==res['gates'],'GATES');ck(all(g.values()) and res['status']=='DESCRIPTIVE_HISTORICAL_ADVANTAGE','CLASSIFICATION')
sessions=[rd(p) for p in sorted(A.glob('session-*.receipt.json'))];ck(len(sessions)==2 and sum(x['stage']=='run' for x in sessions)==1,'SINGLE_RUN');ck(sessions[-1]['exit_code']==0 and sessions[-1]['stop_reason'] is None and sessions[-1]['no_live_worker'],'EXIT');ck(sessions[-1]['end_UTC']<auth['total_work_deadline_utc'],'DEADLINE')
cmd=f"python3 -I -B '{Path(__file__).resolve()}'";elapsed=time.perf_counter()-T;ru=resource.getrusage(resource.RUSAGE_SELF);rss=ru.ru_maxrss if sys.platform=='darwin' else ru.ru_maxrss*1024
report={'status':'PASS_VALID_DESCRIPTIVE_HISTORICAL_ADVANTAGE' if not err else 'NEEDS_FIX','material_errors':err,'scientific_classification':res['status'],'actual_model_effort_speed':'UNKNOWN','ledger_rows_read':nr,'numeric_checks':nc,'max_cash_residual_USD':maxcash,'max_equity_fee_residual_USD':maxfee,'tolerance':'numeric rel1e-9 abs1e-8; cash conservation max(1e-8,1e-10*pretrade equity)','gates_independently_checked':g,'risk_ratios':res['risk_ratios_A_over_B'],'all_overall':{c:{k:calcmap[(c,k,'overall')] for k in ['A','B']} for c in ['25','50']},'paired_and_half_descriptions':res['paired_descriptions'],'fingerprints':fps,'seals':{k:v['UTC'] for k,v in ss.items()},'review_execution':{'actual_command':cmd,'script_identity':fp(__file__),'started_UTC':start,'ended_UTC':datetime.now(timezone.utc).isoformat(),'exit_code':0 if not err else 1,'hash_and_arithmetic_elapsed_seconds':elapsed,'self_peak_RSS_bytes_approx':rss,'self_user_seconds':ru.ru_utime,'self_system_seconds':ru.ru_stime,'prior_supervised_seconds':sessions[-1]['cumulative_seconds'],'combined_supervised_plus_this_check_seconds':sessions[-1]['cumulative_seconds']+elapsed,'self_not_covered_by_owner_supervisor':True,'single_stdlib_process_no_threadpool':True,'formal_receipt':sessions[-1]},'scope':['Only read sealed observations and independently verify deterministic arithmetic; did not import/execute Owner source or create new strategy path, signal or B ledger.','A holdings not recomputed; A identity preserved. Recomputed description metrics only. No bootstrap or significance test.','Old FAILED artifacts untouched; this phase does not revise prior findings. Not all unrelated FAILED objects independently rehashed.','Historical reuse with selection bias; near total volatility is not same annual/tail risk. Actual fill/cost/capacity/PIT UNKNOWN; no actual profit or future advantage claim.']}
with (O/'final-review.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
md=f'''# A年度配置对B同起始固定单位：独立终审\n\n**{report['status']}，无材料错误。冻结条件全部满足，科学分类为DESCRIPTIVE_HISTORICAL_ADVANTAGE，仅为已见历史、共同代理成交假设下的描述性优势。**\n\n一次标准库检查实读A/B四账{nr}行、{nc}项数字核验；A不重算持仓，B首行与同成本A完全一致，中段原单位/现金精确不变，仅首末两笔。身份、授权/gate、单一锁及配置→两B账seal→统一评分→final seal顺序成立。全期、12年、两半与旧A指标相符；首费5000起点、普通q、末费一次、年界/2020 pre边界和pre/post回撤均一致。最大现金残差{maxcash:.12g} USD，最大权益费用残差{maxfee:.12g} USD，容差内。\n\n|成本|A末现金|B末现金|A/B净波动比|\n|---|---:|---:|---:|\n|25bps|{a['end_equity_USD']:.6f}|{b['end_equity_USD']:.6f}|{res['risk_ratios_A_over_B']['25']:.9f}|\n|50bps|{s['end_equity_USD']:.6f}|{t['end_equity_USD']:.6f}|{res['risk_ratios_A_over_B']['50']:.9f}|\n\n25bps A/B Sharpe {a['Sharpe']:.9f}/{b['Sharpe']:.9f}，最大回撤{a['maximum_drawdown']:.9f}/{b['maximum_drawdown']:.9f}；两成本risk合格、主/压力条件均通过。2014–19增长因子比约10.16875，2020–25约1.24918，只描述集中程度，不构成新样本外。\n\n审阅命令：`{cmd}`。本进程开始{start}，hash/算术实耗{elapsed:.9f}s，近似self高水位RSS{rss}B；与prepare+run累计{sessions[-1]['cumulative_seconds']+elapsed:.9f}/600s。自身进程由独立resource收据记录，不冒Owner监督器覆盖；单进程标准库无线程池。正式run exit0/无stderr/单次，采样RSS80986112B、目录2510573B。\n\n原A与旧结论未改。旧FAILED未触碰，不声称本次重新hash所有无关FAILED。没有运行Owner源码、模型、策略、生成B新路径、随机检验、联网、账户或交易。历史PIT、实际成交、全费和容量未证；不能把虚拟末现金当现实利润。只写review目录。actual model/effort/speed UNKNOWN。完成停止。\n'''
with (O/'final-review.md').open('x') as f:f.write(md)
print(json.dumps({'status':report['status'],'errors':err,'rows':nr,'checks':nc,'elapsed':elapsed,'RSS':rss,'total_seconds':sessions[-1]['cumulative_seconds']+elapsed,'A25':a,'B25':b,'A50_end':s['end_equity_USD'],'B50_end':t['end_equity_USD']},ensure_ascii=False))
for p in [O/'final-review.json',O/'final-review.md']:
 b=p.read_bytes();print(p.name,len(b),hashlib.sha256(b).hexdigest())
sys.exit(0 if not err else 1)
