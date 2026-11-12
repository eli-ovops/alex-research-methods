"""Deterministic Budget AST-only checks. No client import/network/TLS/data archives."""
import ast,collections,json,pathlib,sys,types,resource,time,datetime,hashlib
start=time.monotonic();cpu=time.process_time();p=pathlib.Path(__file__).resolve().parent
class Stop(RuntimeError):pass
class Clock:
    def __init__(self):self.now=0.0;self.sleeps=[]
    def monotonic(self):return self.now
    def process_time(self):return 0.0
    def sleep(self,seconds):
        self.sleeps.append(seconds);raise AssertionError('NO_SLEEP_IN_RECEIVED_EVENT_CHECKS')
clock=Clock()
# Stub only virtual clock and resource reads; real deque container, original Budget class body.
stubresource=types.SimpleNamespace(RUSAGE_SELF=0,getrusage=lambda _:types.SimpleNamespace(ru_maxrss=1024))
source=(p/'readonly_core.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Budget')
namespace={'collections':collections,'time':clock,'resource':stubresource,'sys':types.SimpleNamespace(platform='darwin'),'Stop':Stop}
exec(compile(ast.Module(body=[node],type_ignores=[]),'BUDGET_AST_ONLY','exec'),namespace)
Budget=namespace['Budget'];cases=[]
def actual(b):return {'cumulative_CU':b.cu,'methods':b.methods,'window':list(b.window),'window_CU':sum(x[1]for x in b.window),'sleep_calls':list(clock.sleeps)}
def record(name,inputs,expected,result):
    ok=expected==result;cases.append({'name':name,'inputs':inputs,'expected':expected,'actual':result,'status':'PASS'if ok else'FAIL'})
clock.now=0;b=Budget(peak=300);b.delivered(155,0.0);clock.now=.004;b.delivered(155,.004)
record('two155_arrivals_unchanged',[{'CU':155,'arrival':0.0},{'CU':155,'arrival':.004}],{'cumulative_CU':310,'methods':0,'window':[(0.0,155),(.004,155)],'window_CU':310,'sleep_calls':[]},actual(b))
clock.now=0;b=Budget(peak=300);stopped=None
for i in range(20):
    arrival=i*.004;clock.now=arrival
    try:b.delivered(155,arrival)
    except Stop as ex:stopped={'index_1based':i+1,'reason':str(ex)};break
record('twentieth155_stops_but_charged',{'20_costs':155,'arrival_i':'i*0.004'}, {'stop':{'index_1based':20,'reason':'ACTUAL_DELIVERY_PEAK_EXCEEDED_STOP'},'cumulative_CU':3100,'window_CU':3100,'last_arrival':19*.004,'sleep_calls':[]},{'stop':stopped,'cumulative_CU':b.cu,'window_CU':sum(x[1]for x in b.window),'last_arrival':b.window[-1][0],'sleep_calls':clock.sleeps})
for when,window in [(9.999,[(0.0,155),(9.999,155)]),(10.0,[(10.0,155)])]:
    clock.now=0;b=Budget(peak=300);b.delivered(155,0.0);clock.now=when;b.delivered(155,when)
    record('expiry_'+str(when),{'first_arrival':0.0,'next_arrival':when,'cost_each':155},{'cumulative_CU':310,'window':window},{'cumulative_CU':b.cu,'window':list(b.window)})
clock.now=0;b=Budget(cu_limit=310,peak=300);b.delivered(155,0.0);b.delivered(155,.004);at_boundary=b.cu;reason=None
try:b.delivered(1,.008)
except Stop as ex:reason=str(ex)
record('delivered_total_cap_boundary_exceeded_charged',{'cu_limit':310,'delivered':[155,155,1]}, {'exact_boundary':310,'after_failure':311,'reason':'ACTUAL_DELIVERY_CU_CAP_EXCEEDED_STOP'},{'exact_boundary':at_boundary,'after_failure':b.cu,'reason':reason})
clock.now=0;b=Budget(cu_limit=310,peak=300);b.charge(310);reason=None
try:b.charge(1)
except Stop as ex:reason=str(ex)
record('unsent_request_total_cap_precheck',{'cu_limit':310,'request_costs':[310,1]},{'cumulative_CU':310,'methods':1,'reason':'CU_OR_METHOD_BUDGET'},{'cumulative_CU':b.cu,'methods':b.methods,'reason':reason})
clock.now=0;b=Budget(peak=300);b.charge(2000);clock.now=.004;reason=None
try:b.delivered(1100,.004)
except Stop as ex:reason=str(ex)
record('RPC_and_WS_one_shared_window',{'request':{'CU':2000,'clock':0.0},'notification':{'CU':1100,'arrival':.004}},{'cumulative_CU':3100,'methods':1,'window_CU':3100,'reason':'ACTUAL_DELIVERY_PEAK_EXCEEDED_STOP','sleep_calls':[]},{'cumulative_CU':b.cu,'methods':b.methods,'window_CU':sum(x[1]for x in b.window),'reason':reason,'sleep_calls':clock.sleeps})
# Resource/fee/state declarations remain exactly original except timing/capacity definition.
passed=all(x['status']=='PASS'for x in cases)
out={'status':'PASS'if passed else'FAIL','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_sha256':hashlib.sha256(source.encode()).hexdigest(),'executed_scope':'Only AST-extracted Budget class. Entire source/client NOT imported/executed. No network/TLS/market/archive/models.','stubs':'Virtual monotonic/process CPU reads + resource read adapter only; real collections.deque. Stub success not original client/provider availability proof.','cases':cases,'test_process_CPU_seconds':time.process_time()-cpu,'test_wall_seconds':time.monotonic()-start,'test_maxRSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'sleep_calls':clock.sleeps}
(p/'check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':len(cases),'test_process_CPU_seconds':out['test_process_CPU_seconds'],'test_maxRSS_bytes':out['test_maxRSS_bytes']}));sys.exit(0 if passed else 1)
