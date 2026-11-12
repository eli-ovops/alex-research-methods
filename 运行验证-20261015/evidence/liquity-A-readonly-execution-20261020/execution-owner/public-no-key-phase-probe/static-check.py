import ast,pathlib,hashlib,json,time,resource
C=pathlib.Path(__file__).parent;start=time.process_time();s=(C/'probe.py').read_text();tree=ast.parse(s);compile(tree,'UNEXECUTED_PROBE','exec')
core=C.parent/'safe-open-phase-candidate/readonly_core.py';assert hashlib.sha256(core.read_bytes()).hexdigest()=='96f67fec33e5d23edc3e67b029ccd695e23fa747176315a784ad62bde92eb82f'
checks=[]
def passed(n):checks.append({'name':n,'expected':'PASS_STATIC','actual':'PASS_STATIC'})
requests=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='request'];assert len(requests)==1 and [ast.literal_eval(a) for a in requests[0].args]==['HEAD','/'];passed('one_fixed_HEAD_root_no_query_or_JSONRPC')
assert s.count('SystemHTTPSRoute.from_system()')==1 and 'ssl.create_default_context()'in s and "'STRICT_VERIFY_GUARD'"in s and "connection.connect()"in s
assert s.index("connection.connect()")<s.index("connection.request('HEAD'") and s.index('validate_release()\n    lock=')<s.index('spec.loader.exec_module(core)');passed('exact_release_then_reviewed_core_route_strictTLS_before_HEAD')
assert 'self.' not in s and 'prompt_endpoint('not in s and 'SecretEndpoint('not in s and 'core.RPC('not in s and 'core.HeadStream('not in s and 'os.environ'not in s and 'sys.argv'not in s;passed('no_account_input_RPC_stream_environment_or_argument_read')
assert "signal.alarm(20)"in s and '15-(time.monotonic()-request_start)'in s and s.count('min(5,remaining())')==2 and "lock.open('x')"in s and "(HERE/'result.json').open('x')"in s;passed('onceguard_wall_request_socket_guards_STATIC')
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'str','repr'} for n in ast.walk(tree))
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'read','getheader','getheaders','getenv'} for n in ast.walk(tree));passed('no_error_text_header_body_or_private_config_serialization')
assert "phase=value if value in PHASES else 'OTHER'"in s and 'core.safe_transport_diagnostic' in s and 'response.close()'in s
assert not any(isinstance(n,(ast.For,ast.While)) for n in ast.walk(tree));passed('fixed_phase_safe_diagnostic_no_retry_redirect_or_fallback_loop')
r={'status':'PASS_STATIC_UNEXECUTED_PROBE','checks':checks,'core_sha256':hashlib.sha256(core.read_bytes()).hexdigest(),'probe_executed':False,'network_TLS_route_config_reads':0,'process_body_CPU_seconds':time.process_time()-start,'maxrss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(C/'static-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
