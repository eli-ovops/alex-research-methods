from pathlib import Path
import hashlib,json,difflib
D=Path(__file__).resolve().parents[2]; O=D/'execution-owner'; C=Path(__file__).parent
sha=lambda b:hashlib.sha256(b).hexdigest()
base=(O/'readonly_collector.py').read_text();core=(O/'offline-throughput-window-candidate/readonly_core.py').read_bytes()
assert sha((O/'readonly_core.py').read_bytes())=='a2f7d56b1f90c2ee535679d3d48c461a30f2ec2e92001227887312c5b3508436'
assert sha(base.encode())=='4dd5774bf4d5fea066bb55714907615c208009065582db70e80f824f843a6e74'
assert sha(core)=='54b09fc1d32186dfca56c0a8eb15b6172b335693824489676ba47c627c7af5bc'
(C/'readonly_core.py').write_bytes(core)
s=base.replace('remaining-preflight-20261020-06','throughput10s-attempt-01').replace('start-A-remaining-preflight-run06.command','start-A-throughput10s-attempt-01.command').replace('root/run06-preinput-release.json','root/throughput10s-preinput-release.json').replace('root/remaining-preflight-run06-release.json','root/throughput10s-formal-release.json')
# Historical authorization checks stay intact; the new overlay is checked separately.
s=s.replace('def effective_resource_limits(c,release):','def historical_resource_limits(c,release):',1)
helper='''LOCAL_WINDOW={'local_window_seconds':10.0,'local_window_capacity_CU':3000,'nominal_rate_CU_s':300,'scope':'PROJECT_CONSERVATIVE_NOT_PROVIDER_BUCKET_OR_SHARED_BALANCE'}
EXPECTED_T0='2026-10-21T00:00:00Z'
EXPECTED_T1='2026-11-04T00:00:00Z'

def fixed_observation_window(c,now=None):
    now=dt.datetime.now(dt.timezone.utc) if now is None else now
    if c.get('expected_T0')!=EXPECTED_T0 or c.get('expected_T1')!=EXPECTED_T1:raise Stop('FIXED_OBSERVATION_IDENTITY')
    t0=dt.datetime.fromisoformat(EXPECTED_T0.replace('Z','+00:00'));t1=dt.datetime.fromisoformat(EXPECTED_T1.replace('Z','+00:00'))
    nxt=(now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
    if now>=t0 or nxt!=t0 or t1-t0!=dt.timedelta(days=14):raise Stop('FIXED_T0_CANNOT_BE_FULLY_COVERED')
    return t0,t1

def integration_identity(c,r,now=None):
    if c.get('status')!='ROOT_BOUND_TECHNICAL_CONTINUATION' or r.get('run_id')!=RUN_ID:raise Stop('TECHNICAL_DRAFT_OR_OLD_RUN')
    if c.get('local_throughput')!=LOCAL_WINDOW or r.get('local_throughput')!=LOCAL_WINDOW:raise Stop('LOCAL_WINDOW_METADATA')
    u=c.get('shared_prior_usage',{});cpu=r.get('prior_CPU_upper_bound_seconds')
    if type(u.get('cu'))is not int or u['cu']<32734 or type(u.get('methods'))is not int or u['methods']<62 or type(cpu)not in(int,float) or not 6789<=cpu<18000:raise Stop('CUMULATIVE_USAGE_DECREASE')
    fixed_observation_window(c,now)

def effective_resource_limits(c,release):
    # Validate the immutable historical resource-flow record with its historical limits.
    historical=json.loads(pathlib.Path(c['resource_flow_authorization']['path']).read_bytes())
    old_release=dict(release,effective_limits=historical['effective_limits'])
    base=historical_resource_limits(c,old_release)
    src=c.get('technical_continuation_overlay',{})
    if src.get('path')!=str(UNIT/'root/throughput10s-technical-overlay.json'):raise Stop('TECHNICAL_OVERLAY_PATH')
    path=pathlib.Path(src['path'])
    if not path.is_file():raise Stop('TECHNICAL_OVERLAY_MISSING')
    raw=path.read_bytes()
    if digest(raw)!=src.get('sha256') or release.get('technical_overlay_sha256')!=digest(raw):raise Stop('TECHNICAL_OVERLAY_HASH')
    a=json.loads(raw);integration_identity(c,release)
    if a.get('status')!='ROOT_AUTHORIZED_TECHNICAL_CONTINUATION' or a.get('run_id')!=RUN_ID or a.get('prior_usage_reset')is not False:raise Stop('TECHNICAL_OVERLAY_DRAFT_OR_SCOPE')
    if a.get('historical_resource_authorization')!=c['resource_flow_authorization'] or a.get('original_resource_authorization')!=c['resource_authorization'] or a.get('peak_authorization')!=c['supplemental_peak_authorization']:raise Stop('TECHNICAL_OVERLAY_PARENT')
    acceptance=c['integration_plan_acceptance'];p=pathlib.Path(acceptance['path'])
    if digest(p.read_bytes())!=acceptance['sha256'] or a.get('integration_plan_acceptance')!=acceptance:raise Stop('TECHNICAL_ACCEPTANCE_BINDING')
    if a.get('local_throughput')!=LOCAL_WINDOW or a.get('expected_T0')!=EXPECTED_T0 or a.get('expected_T1')!=EXPECTED_T1 or a.get('retained_usage')!=c['shared_prior_usage']:raise Stop('TECHNICAL_OVERLAY_METADATA')
    # Only the bounded startup interval is overlaid, never the observation/resource/economic caps.
    changes=a.get('startup_window',{});keys={'startup_window_start_UTC','startup_absolute_stop_UTC','input_entry_must_be_ready_by_UTC'}
    if set(changes)!=keys:raise Stop('TECHNICAL_STARTUP_FIELDS')
    ts=lambda x:dt.datetime.fromisoformat(x.replace('Z','+00:00')).timestamp()
    start,end,ready=[ts(changes[k]) for k in ['startup_window_start_UTC','startup_absolute_stop_UTC','input_entry_must_be_ready_by_UTC']]
    now=time.time()
    if not start<=now<ready<=end-1200 or end-start>7200 or end>ts(EXPECTED_T0):raise Stop('TECHNICAL_STARTUP_EXPIRED_OR_UNBOUNDED')
    limits=dict(base,**changes)
    if release.get('effective_limits')!=limits:raise Stop('TECHNICAL_EFFECTIVE_LIMITS')
    return limits


'''
s=s.replace('def load_admission(path,preinput=False):',helper+'def load_admission(path,preinput=False):')
s=s.replace("b=Bindings(path);c=b.config","b=Bindings(path);c=b.config",1)
s=s.replace("if type(prior_cpu) not in (int,float) or not 6526<=prior_cpu", "if type(prior_cpu) not in (int,float) or not 6789<=prior_cpu")
s=s.replace("usage.get('retained_local_CU_reserved')!=1824", "usage.get('retained_local_CU_reserved')!=c['shared_prior_usage']['cu']").replace("usage.get('retained_local_method_attempts')!=41", "usage.get('retained_local_method_attempts')!=c['shared_prior_usage']['methods']")
s=s.replace("if state.get('cu')!=1824 or state.get('methods')!=41:","if type(state.get('cu'))is not int or state['cu']<32734 or type(state.get('methods'))is not int or state['methods']<62:")
s=s.replace("floor<6526", "floor<6789").replace("ledger.get('retained_CU')!=1824", "ledger.get('retained_CU')!=state['cu']").replace("ledger.get('retained_method_attempts')!=41", "ledger.get('retained_method_attempts')!=state['methods']")
s=s.replace("if ledger.get('authorization_sha256')!=c['resource_flow_authorization']['sha256']", "if ledger.get('authorization_sha256')!=c['technical_continuation_overlay']['sha256']")
s=s.replace("    r=json.loads(path.read_bytes())\n    if r.get('status')", "    r=json.loads(path.read_bytes())\n    integration_identity(binding.config,r)\n    if r.get('status')",1)
# Fixed absolute observation dates at all projection/admission sites.
s=s.replace("now=dt.datetime.now(dt.timezone.utc);t0=(now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)","now=dt.datetime.now(dt.timezone.utc);t0,t1=fixed_observation_window(c,now)")
s=s.replace("lower_now=dt.datetime.now(dt.timezone.utc);lower_t0=(lower_now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)","lower_now=dt.datetime.now(dt.timezone.utc);lower_t0,_=fixed_observation_window(c,lower_now)")
s=s.replace("now=dt.datetime.now(dt.timezone.utc);t0=(now+dt.timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0);t1=t0+dt.timedelta(days=14)","now=dt.datetime.now(dt.timezone.utc);t0,t1=fixed_observation_window(c,now)")
# Previous replace may have left a redundant t1 assignment (same fixed interval); remove it.
s=s.replace("t0,t1=fixed_observation_window(c,now);t1=t0+dt.timedelta(days=14)","t0,t1=fixed_observation_window(c,now)")
s=s.replace("details={'forecast_kind':", "details={'local_throughput':dict(LOCAL_WINDOW),'forecast_kind':")
# Validate all publication gates before creating the fresh prep run or prompting.
s=s.replace("    deadline=dt.datetime(2026,10,20,10,29,58,tzinfo=dt.timezone.utc).timestamp();arm_startup_alarm(deadline)\n    RUN_DIR.mkdir", "    b=load_admission(binding_path,preinput=True);deadline=startup_timestamp(b.limits);arm_startup_alarm(deadline)\n    RUN_DIR.mkdir",1)
s=s.replace("    started_ns=time.monotonic_ns();b=None;tls=None", "    started_ns=time.monotonic_ns();tls=None")
s=s.replace("        b=load_admission(binding_path,preinput=True);c=b.config;limits=b.limits", "        c=b.config;limits=b.limits")
s=s.replace("    deadline=dt.datetime(2026,10,20,10,29,58,tzinfo=dt.timezone.utc).timestamp()\n    arm_startup_alarm(deadline)\n    b=load_admission(binding_path);c=b.config;limits=b.limits", "    b=load_admission(binding_path);c=b.config;limits=b.limits\n    deadline=startup_timestamp(limits);arm_startup_alarm(deadline)")
(C/'readonly_collector.py').write_text(s)
c=json.loads((O/'bindings-remaining-preflight-run06.json').read_bytes());c.update(status='DRAFT_NOT_RELEASED_OR_RUNNABLE',shared_prior_usage={'cu':32734,'methods':62,'cpu':None},shared_prior_usage_scope='Retain at least32734CU/62methods; Root final CPU ledger >=6789; all historical disk retained; no reset',expected_T0='2026-10-21T00:00:00Z',expected_T1='2026-11-04T00:00:00Z',local_throughput={'local_window_seconds':10.0,'local_window_capacity_CU':3000,'nominal_rate_CU_s':300,'scope':'PROJECT_CONSERVATIVE_NOT_PROVIDER_BUCKET_OR_SHARED_BALANCE'})
c['static_release_required_at']=str(D/'root/throughput10s-formal-release.json')
for key,name in [('quota_source','throughput10s-fresh-quota.json'),('prior_CPU_source','throughput10s-cumulative-CPU-ledger.json'),('technical_continuation_overlay','throughput10s-technical-overlay.json')]:c[key]={'path':str(D/'root'/name),'sha256':'DRAFT_NOT_BOUND'}
p=D/'root/throughput-integration-plan-final-acceptance.json';c['integration_plan_acceptance']={'path':str(p),'sha256':sha(p.read_bytes())}
c['free_working_cap_scope']='Retain32734CU/62methods, actualfree stricterthan25M; exact new Root quota required, no rounded balance assertion'
(C/'binding.DRAFT.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
launcher="#!/bin/zsh\n# NON-ACTIVATED TEMPLATE; user personally starts only after exact Root publication.\nexec '/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/.venv/bin/python' -B -E -S '"+str(O/'readonly_collector.py')+"' --live '"+str(O/'bindings-throughput10s-attempt-01.json')+"'\n"
(C/'launcher.NONACTIVATED.txt').write_text(launcher)
(C/'technical-overlay.DRAFT.json').write_text(json.dumps({'status':'DRAFT_NOT_RELEASED','run_id':'throughput10s-attempt-01','historical_resource_authorization':c['resource_flow_authorization'],'original_resource_authorization':c['resource_authorization'],'peak_authorization':c['supplemental_peak_authorization'],'integration_plan_acceptance':c['integration_plan_acceptance'],'prior_usage_reset':False,'retained_usage':c['shared_prior_usage'],'local_throughput':c['local_throughput'],'expected_T0':c['expected_T0'],'expected_T1':c['expected_T1'],'startup_window':{'startup_window_start_UTC':'DRAFT_ROOT_UTC_REQUIRED','startup_absolute_stop_UTC':'DRAFT_ROOT_UTC_REQUIRED','input_entry_must_be_ready_by_UTC':'DRAFT_ROOT_UTC_REQUIRED'}},ensure_ascii=False,indent=2)+'\n')
(C/'release-schema.DRAFT.json').write_text(json.dumps({'status':'DRAFT_NOT_RELEASED','run_id':'throughput10s-attempt-01','bindings_sha256':'EXACT_PUBLISHED_BINDING_REQUIRED','reviewed_code_sha256':{x:'EXACT_SHA256_REQUIRED' for x in ['readonly_core.py','readonly_collector.py','start-A-throughput10s-attempt-01.command']},'local_throughput':c['local_throughput'],'technical_overlay_sha256':'EXACT_ROOT_OVERLAY_REQUIRED','effective_limits':'EXACT_HISTORICAL_CAPS_PLUS_APPROVED_STARTUP_ONLY','prior_CPU_upper_bound_seconds':'ROOT_DEDUP_LEDGER_AT_LEAST6789','new_active_work_budget':'RETAIN_ORIGINAL_ACTIVE_BUDGET_GUARD','resource_flow_authorization_sha256':c['resource_flow_authorization']['sha256'],'supplemental_peak_authorization_sha256':c['supplemental_peak_authorization']['sha256'],'authorized_peak_CU_per_second':300,'no_key_preparation':'FORMAL_ONLY_EXACT_RUN_PREP_PATH_HASH'},indent=2)+'\n')
pairs=[('readonly_core.py',(O/'readonly_core.py').read_text(),core.decode()),('readonly_collector.py',base,s),('bindings-throughput10s-attempt-01.json',(O/'bindings-remaining-preflight-run06.json').read_text(),(C/'binding.DRAFT.json').read_text()),('start-A-throughput10s-attempt-01.command',(O/'start-A-remaining-preflight-run06.command').read_text(),launcher)]
(C/'review-package.diff').write_text(''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='BASE/'+n,tofile='CANDIDATE/'+n)) for n,a,b in pairs))
print('CANDIDATE_BUILT_NO_EXECUTION')
