# coding: utf-8
"""Independent small-artifact failure acceptance; never opens market/NPZ payload."""
import pathlib,json,hashlib,time,datetime,resource
start=time.perf_counter();cpu=time.process_time();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
s=pathlib.Path(__file__).resolve().parents[1];e=s/'execution';r=s/'review';fps={}
def fp(p):
 p=pathlib.Path(p)
 assert p.suffix not in ('.gz','.npz'), 'NO_MARKET_PAYLOAD'
 b=p.read_bytes();v={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};fps[str(p)]=v;return v
def read(p):fp(p);return json.loads(pathlib.Path(p).read_text())
c=read(e/'execution-completion.json');seal=read(e/'partial-output-seal.json');source=read(e/'source-seal.json');gate=read(s/'preflight-review/gate.json');a=read(s/'root/authorization-and-scope.json');config=read(e/'config.json')
assert fp(e/'execution-completion.json')['sha256']=='5b9549dc47f7bb67130599f160adfc036ca465ab3da41a978ea8611084c42a38'
for mapping in [c['inputs'],seal['small_artifacts'],source['inputs'],gate['source_inputs'],gate['preflight_inputs']]:
 for p,v in mapping.items():assert fp(p)==v,(p,'HASH_MISMATCH')
assert source['inputs']==gate['source_inputs']
assert fp(e/'partial-output-seal.json')==c['partial_output_seal']
assert fp(e/'result-report.md')==c['report']
lock=read(e/'formal-started.lock');run=read(e/'session-run.json');stop=read(e/'worker-formal-STOP.json');health=read(e/'session-health.json')
assert fp(s/'preflight-review/gate.json')==lock['identity'];assert gate['allow_five_date_unit'] is True
assert gate['sealed_UTC']<lock['UTC']<run['started_UTC']<stop['UTC']<run['ended_UTC']<c['UTC']
assert run['exit_code']==1 and run['no_active_worker'] and run['status']=='STOP'
assert stop['code']=='TARGET_CLOCK_FORMAT'
assert abs(run['elapsed_seconds']+health['elapsed_seconds']-run['cumulative_seconds'])<1e-8
assert run['sampled_combined_peak_RSS_bytes']<=536870912 and run['disk_bytes']<=1073741824
assert run['ended_UTC']<a['work_deadline_utc']
cohort=read(pathlib.Path(a['fixed_cohort']['path']));objs={o['Key'].split('/')[-1][:8]:o for o in cohort['objects']}
downloads={};total=0
for day in cohort['calendar_dates_chosen_before_any_new_prices_or_outcomes'][1:]:
 d=read(e/(day+'-download.json'));o=objs[day]
 assert d['requests']==1 and d['status']==200 and d['expected_ETag']==o['ETag']==d['headers']['ETag']
 assert int(o['Size'])==d['bytes']==int(d['headers']['Content-Length'])
 assert pathlib.Path(d['path']).stat().st_size==d['bytes']
 assert d['sha256']==c['download_stream_identities'][day]['sha256'];downloads[day]=d;total+=d['bytes']
assert total==768134748
qcs={}
for day in ['20240101','20240401','20240701','20241001']:
 q=read(e/(day+'-QC.json'));qcs[day]=q
 assert q['gzip_EOF_CRC'] and q['planned_windows']==1437
 assert q['scorable']+q['unscorable']==1437 and q['scorable']<=q['current_past_eligible']<=1437
 assert q['scorable']>=.8*1437 and q['target_backward']==0 and q['strict_target_BBO_invalid']==0
 if day!='20240101':assert q['identity']=={'bytes':downloads[day]['bytes'],'sha256':downloads[day]['sha256']}
absent=['20250101-QC.json','all-source-and-QC-seal.json','weights-and-scaling.json','weights-seal.json','predictions-and-signals-seal.json','evaluation-results.json','result-seal.json','20241001-sealed-predictions-and-signals.npz','20250101-sealed-predictions-and-signals.npz']
assert not any((e/n).exists() for n in absent)
assert c['actual_fit_counts']=={'A':0,'B':0} and c['actual_test_prediction_stages']==c['actual_scoring_bootstrap_cost_stages']==0
adapter=(e/'adapter.py').read_text();supervisor=(e/'supervise.py').read_text()
assert adapter.index("data[ds]=scan(")<adapter.index("models[name]=fit(")
assert "raise RuntimeError('TARGET_CLOCK_FORMAT')" in adapter and "child.wait()" in supervisor
fp(pathlib.Path(__file__))
resource_rec={'started_UTC':started,'ended_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,'CPU_seconds':time.process_time()-cpu,'self_ru_maxrss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'self_ru_maxrss_unit':'bytes on macOS; KiB on Linux','review_small_checks_extra_conservative_charge_seconds':1.0,'owner_charged_seconds':c['charged_before_independent_acceptance_seconds'],'not_covered_by_owner_supervisor':True,'new_network_or_market_decode_or_model_or_statistics':0}
resource_rec['total_charged_including_this_checker_and_extra_second']=resource_rec['owner_charged_seconds']+resource_rec['elapsed_seconds']+1
assert resource_rec['total_charged_including_this_checker_and_extra_second']<1800
out={'status':'PASS_FAILURE_CONTAINMENT_TECHNICAL_DATA_UNDETERMINED','scientific_status':'TECHNICAL_DATA_UNDETERMINED_NO_MODEL_RESULT','mustfix_for_accepting_stop':[],'UTC':resource_rec['ended_UTC'],'actual_model_effort_route':'UNKNOWN','inputs':fps,'facts':{'four_new_GETs':4,'new_compressed_bytes':total,'EOF_CRC_completed_dates':list(qcs),'scorable_counts':{k:v['scorable'] for k,v in qcs.items()},'last_date':'20250101 complete compressed GET; decoded scan/EOF CRC incomplete','stop':stop,'A_fit':0,'B_fit':0,'prediction_scoring_bootstrap_cost_stages':0,'absent_outputs_verified':absent,'unique_formal_lock':lock,'session_exit':1,'worker_no_active_basis':'Known-PID supervisor finally waits/reaps child and terminal receipt, not a broad process scan','stream_source_SHA_basis':'Owner stream receipt plus small-artifact identities and local file size only; reviewer did not hash/decompress market sources'},'source_locators':{'adapter.py:85-90':'D-separated fixed 9 decimal-digit parser; implementation format constraint','adapter.py:152-163':'All five scans must finish before train concatenation or fit','adapter.py:213-221':'Sanitized STOP and SystemExit(1)','supervise.py:32':'Exclusive x-mode single formal lock','supervise.py:50-60':'Exception-safe terminate/wait/kill cleanup'},'interpretation':['The actual rejected token and row were not retained. Legal format variant versus malformed source clock remains UNKNOWN; neither dataset bad nor model NOT_SUPPORTED is established.','Four earlier dates remain partial preparation evidence. Do not discard fifth date, reduce test set, repair parser or rerun under this completed failed once-unit.','No candidate score exists: no incremental predictive, quote-space, inverse native PnL, ROI, stable edge, actual fill, fee or capacity inference.','No old FAILED or original proposal was written by this reviewer. Their full historical corpus was not rescanned.','No requirement to make 10bps combined score mean monotonic: signal subset/same-trade score properties are distinct; no costs were reached here.'],'resource':resource_rec,'review_limits':'Small original receipts, seals, source/control flow, filesystem output absence and deterministic count checks only. No raw market token/NPZ read, full source hash/CRC recomputation, model load, prediction, MSE, cost or bootstrap.'}
(r/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(r/'audit.md').write_text('''# 独立失败原件验收\n\n结论：**PASS_FAILURE_CONTAINMENT_TECHNICAL_DATA_UNDETERMINED**。唯一正式作业按失败停止，原件和停止范围可接受；并非模型假设 NOT_SUPPORTED，也不能认定源数据损坏。无必须修改项才能接受本次停止。\n\n四个固定新 GET 均为一次 HTTP200，长度/ETag与冻结对象一致，合计 768,134,748 B；已核小回执SHA、source/config/gate/partial seal绑定及本地文件长度，没有重hash或解压行情。20240101、0401、0701、1001的小QC声明实际读至gzip EOF/CRC；对应可评分窗口1282/1434/1392/1402，各以1437为分母，合格+不合格守恒。第五日压缩下载完整不等于已完成gzip校验。\n\n20250101扫描报 TARGET_CLOCK_FORMAT。adapter.py:85–90只接受D分隔、9位小数，这是适配实现约束；未留拒绝token/行号，合法变体或坏时钟仍UNKNOWN。源码152–163明确五日全扫描返回后才fit；原件目录无all-source seal、权重、预测/信号seal、evaluation/results，故A/B拟合、预测、bootstrap、成本评分均0。不得删第五日救成一日测试，不修改本次规则或重跑。\n\n单次exclusive lock绑定实际gate；正式00:55:37.390784→00:58:12.153520UTC，exit1。监督器finally按已知child终止/等待，终端回执无活worker；不将空stderr当成功。health+formal154.978271501s，Owner另保守5s；合并采样RSS66,568,192B、执行盘768,588,697B，均在scope内。独立小原件检查的实耗/selfRSS另存audit.json，不冒称由Owner监督器覆盖。\n\n只有失败容纳验收通过：预测优势、净收益、原生逆向合约盈亏、稳定性、现实成交/费用及容量均未判定。旧FAILED和冻结提案未改；不声称扫描旧证据全库以证明不变。实际模型/effort/route UNKNOWN。\n''')
for n in ['audit.json','audit.md']:
 p=r/n;print(json.dumps({'path':str(p),**fp(p)},ensure_ascii=False))
print(json.dumps({'resource':resource_rec,'exit':0},ensure_ascii=False))
