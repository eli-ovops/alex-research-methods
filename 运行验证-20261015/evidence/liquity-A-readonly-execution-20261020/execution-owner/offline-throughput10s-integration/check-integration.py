import ast,datetime as dt,json,pathlib,hashlib,types,math,collections,tempfile,resource,time,socket
C=pathlib.Path(__file__).parent;start=time.process_time();wall=time.monotonic()
socket.create_connection=lambda *a,**k:(_ for _ in ()).throw(AssertionError('NETWORK_FORBIDDEN'))
text=(C/'readonly_collector.py').read_text();tree=ast.parse(text);ct=ast.parse((C/'readonly_core.py').read_text())
class Stop(Exception):pass
env={'dt':dt,'Stop':Stop,'RUN_ID':'throughput10s-attempt-01','time':time,'math':math,'deque':collections.deque}
names={'integration_identity','fixed_observation_window'}
body=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'LOCAL_WINDOW','EXPECTED_T0','EXPECTED_T1'} for t in n.targets) or isinstance(n,ast.FunctionDef) and n.name in names]
exec(compile(ast.Module(body=body,type_ignores=[]),'PURE_LOGIC_ONLY','exec'),env)
now=dt.datetime(2026,10,20,12,tzinfo=dt.timezone.utc)
c=json.loads((C/'binding.DRAFT.json').read_text());good=dict(c,status='ROOT_BOUND_TECHNICAL_CONTINUATION');r={'run_id':env['RUN_ID'],'local_throughput':c['local_throughput'],'prior_CPU_upper_bound_seconds':6789}
checks=[]
def check(name,fn):fn();checks.append({'name':name,'expected':'PASS','actual':'PASS'})
def reject(fn):
 try:fn()
 except Stop:return
 raise AssertionError('SHOULD_REJECT')
def prior():
 env['integration_identity'](good,r,now)
 for key,value in [('cu',32733),('methods',61)]:
  v=dict(good,shared_prior_usage=dict(good['shared_prior_usage'],**{key:value}));reject(lambda:env['integration_identity'](v,r,now))
 reject(lambda:env['integration_identity'](good,dict(r,prior_CPU_upper_bound_seconds=6788),now))
check('cumulative32734_62_CPU6789_and_decrease_rejection',prior)
def drafts():
 reject(lambda:env['integration_identity'](c,r,now));reject(lambda:env['integration_identity'](good,dict(r,run_id='remaining-preflight-20261020-06'),now))
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_release');src=ast.get_source_segment(text,node)
 assert "if not path.is_file():raise Stop('STATIC_RELEASE_MISSING')" in src
 assert "STATIC_RELEASE_CODE_HASH" in src and "digest(p.read_bytes())" in src
 assert "integration_identity(binding.config,r)" in src
check('DRAFT_oldrun_reject_missingrelease_codehash_gate_STATIC',drafts)
def dates():
 assert env['fixed_observation_window'](good,now)[0].isoformat()=='2026-10-21T00:00:00+00:00'
 reject(lambda:env['fixed_observation_window'](dict(good,expected_T1='2026-11-05T00:00:00Z'),now))
 for d in [dt.datetime(2026,10,19,12,tzinfo=dt.timezone.utc),dt.datetime(2026,10,21,tzinfo=dt.timezone.utc)]:reject(lambda:env['fixed_observation_window'](good,d))
 assert text.count('fixed_observation_window(c,now)')>=2 and 'fixed_observation_window(c,lower_now)' in text
check('fixed_absoluteT0T1_late_and_implicit_shift_rejection',dates)
# Only Budget class AST is extracted; do not import or run any client.
bnode=next(n for n in ct.body if isinstance(n,ast.ClassDef) and n.name=='Budget')
print(ast.unparse(bnode),file=open(C/'budget-extracted-review.txt','w'))
# Wiring/unchanged economic and coverage paths are TEXT/AST identity, never live proof.
def paths():
 assert "root/throughput10s-preinput-release.json" in text and "root/throughput10s-formal-release.json" in text
 for x in ['no-key-preparation.once.lock','input-entry.once.lock','live-once.lock']:assert "'"+x+"'" in text
 assert text.count(".open('x')")>=4
 assert 'remaining-preflight-20261020-06' not in text
 prep=ast.get_source_segment(text,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepare_input'))
 assert prep.index('b=load_admission(binding_path,preinput=True)')<prep.index('RUN_DIR.mkdir')
check('new_run_three_exclusive_once_paths_and_preTLS_gate_STATIC',paths)
def preserved():
 base=(C.parents[0]/'readonly_collector.py').read_text();bt=ast.parse(base)
 for name in ['Bindings','Scanner','qualify','timely','forward_head','completed_event_audit','independent_preflight_reference','set_process_CPU_limit','check_input_window']:
  a=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
  b=next(n for n in bt.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
  assert ast.dump(a)==ast.dump(b),name
 assert 'signal.alarm(0)\n        state.update(status=\'ARMED_ACTIVE_PROCESS\'' in text
 assert 'while dt.datetime.now(dt.timezone.utc)<t1:' in text
 assert "local_throughput':dict(LOCAL_WINDOW)" in text
check('fiveRuntime_fullstate_WS_fence_timing_backlog_resources_economic_paths_preserved_STATIC',preserved)
# virtual clock wait branch needs resource/time globals used by the accepted class.
def wait_branch():
 import sys
 class Clock:
  def __init__(self):self.now=0.;self.wait=[]
  def monotonic(self):return self.now
  def process_time(self):return 0.
  def sleep(self,n):self.wait.append(n);self.now+=n
 clock=Clock();ns={'time':clock,'collections':collections,'resource':resource,'sys':sys,'Stop':Stop}
 exec(compile(ast.Module(body=[bnode],type_ignores=[]),'BUDGET_AST_ONLY','exec'),ns)
 b=ns['Budget'](peak=300,cpu=18000,state={'cu':32734,'methods':62,'cpu':6789})
 b.delivered(2990,0.);saved=list(b.window);clock.now=9.999;b.charge(26)
 assert abs(clock.now-10.009)<1e-8 and len(clock.wait)==1
 assert saved==[(0.,2990)] and b.cu==35750 and b.methods==63 and list(b.window)==[(clock.now,26)]
 checks.append({'name':'virtual_wait_details','expected':'One wait to >=10.0; unchanged delivery timestamp, retained CU/methods','actual':{'wait':clock.wait,'clock':clock.now,'original_arrival':saved,'CU':b.cu,'methods':b.methods}})
check('new_10second_outgoing_wait_branch_not_old7cases',wait_branch)
# Test used-once behavior in a temporary, unrelated fixture directory, never real run locks.
def exclusive():
 with tempfile.TemporaryDirectory() as td:
  p=pathlib.Path(td)/'fixture.once';p.open('x').close()
  try:p.open('x')
  except FileExistsError:return
  raise AssertionError('ONCE_REUSED')
check('used_fixture_once_rejected',exclusive)
result={'status':'PASS_OFFLINE_AFFECTED_INTEGRATION_CHECKS_NOT_LIVE','checks':checks,'scope':'AST pure new identity/date logic; virtual wait; static unchanged gate identity; temporary fixture once. No complete client import/entry, no same-code7checks repeated, no real source records or archive read, no network.','process_CPU_seconds':time.process_time()-start,'wall_seconds':time.monotonic()-wall,'maxrss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(C/'checks-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
