"""Offline fixtures only. No network, credentials, deployment or profit evidence."""
import pathlib,tempfile,unittest,json,gzip,unittest.mock as mock
from readonly_core import *
from readonly_collector import oracle_price,qualify,Scanner,LATEST_FIELDS,forecast

class ABI(unittest.TestCase):
    def test_keccak_vectors_and_saved_real_ABI(self):
        self.assertEqual(keccak256(b'').hex(),'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470')
        self.assertEqual(keccak256(b'transfer(address,uint256)').hex()[:8],'a9059cbb')
        p=pathlib.Path('/Volumes/EXTERNAL/亚力克斯 /运行验证-20261015/evidence/liquity-official-deployment-binding-20261020/root/sourcify-record.body')
        b=p.read_bytes();self.assertEqual(digest(b),'002c37f8674d4fef6fb721a70d1ad26af02ee4a678aba0ae4bdd27222265f202');j=json.loads(b)
        for entry in j['signatures']['function']:
            self.assertEqual('0x'+keccak256(entry['signature'].encode()).hex()[:8],entry['signatureHash4'])
        fn=abi_method(j,'getLatestTroveData')[1]
        self.assertEqual([x['name'] for x in fn['outputs'][0]['components']],LATEST_FIELDS)
        for absent in ['MCR','priceFeed','addressesRegistry','getTroves']:
            with self.assertRaises(Stop):abi_method(j,absent)
    def test_aggregate_encoding_offsets(self):
        encoded=rawhex(aggregate3('0x82ad56cb',[('0x'+'11'*20,'0x12345678'),('0x'+'22'*20,'0x')]))
        self.assertEqual(encoded[:4].hex(),'82ad56cb');z=encoded[4:]
        self.assertEqual(int.from_bytes(z[0:32],'big'),32);self.assertEqual(int.from_bytes(z[32:64],'big'),2)
        self.assertEqual(int.from_bytes(z[64:96],'big'),64);self.assertEqual(int.from_bytes(z[96:128],'big'),224)
        self.assertEqual(z[128:160],word(int('11'*20,16)))
    def test_aggregate_decode_return_fixture(self):
        a=word(1)+word(64)+word(32)+word(99);b=word(0)+word(64)+word(0)
        result='0x'+(word(32)+word(2)+word(64)+word(64+len(a))+a+b).hex()
        self.assertEqual(decode_aggregate3(result,2),[(True,'0x'+word(99).hex()),(False,'0x')])
        with self.assertRaises(Stop):decode_aggregate3(result,3)
        with self.assertRaises(Stop):decode_aggregate3('0x'+(word(32)+word(1)+word(0)).hex(),1)
    def test_static_length_address_and_status(self):
        self.assertEqual(uints('0x'+word(2).hex(),1),(2,))
        with self.assertRaises(Stop):uints('0x00',1)
        with self.assertRaises(Stop):address('0x'+word(2**160).hex())

class Safety(unittest.TestCase):
    def test_secret_not_represented_and_schema_rejects(self):
        e=SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/SECRET_FIXTURE_ABC')
        self.assertNotIn('SECRET_FIXTURE_ABC',repr(e));self.assertNotIn(b'SECRET_FIXTURE_ABC',e.redact(b'error SECRET_FIXTURE_ABC https://eth-mainnet.g.alchemy.com/v2/SECRET_FIXTURE_ABC'))
        for u in ['http://eth-mainnet.g.alchemy.com/v2/x','https://eth-mainnet.g.alchemy.com.evil/v2/x','https://u:[REDACTED_EMAIL]/v2/x','https://eth-mainnet.g.alchemy.com/v2/x?key=x','https://eth-mainnet.g.alchemy.com:443/v2/x','https://eth-mainnet.g.alchemy.com/v2/x/y']:
            with self.assertRaises(Stop):SecretEndpoint(u)
    def test_method_allowlist_before_network(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            e=SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/SECRET_FIXTURE_ABC');rpc=RPC(e,Budget(),Evidence(tmp,tmp),{'eth_call':26})
            for method in ['eth_sendRawTransaction','eth_sendTransaction','eth_sign','personal_sign','wallet_sendCalls','eth_estimateGas','debug_traceTransaction']:
                with self.assertRaises(Stop):rpc.call(method,[])
            self.assertEqual(rpc.budget.methods,0)
    def test_exception_redaction_to_disk(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            e=SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/SECRET_FIXTURE_ABC');rpc=RPC(e,Budget(),Evidence(tmp,tmp),{'eth_chainId':0})
            rpc.opener=mock.Mock();rpc.opener.open.side_effect=RuntimeError('SECRET_FIXTURE_ABC')
            with self.assertRaisesRegex(Stop,'TRANSPORT_RuntimeError'):rpc.call('eth_chainId',[])
            alltext=b''.join(gzip.decompress(p.read_bytes()) for p in pathlib.Path(tmp).glob('*.gz'))
            self.assertNotIn(b'SECRET_FIXTURE_ABC',alltext)
    def test_method_CU_peak_CPU_RAM_disk(self):
        b=Budget(cu_limit=30,method_limit=1);b.charge(26)
        with self.assertRaises(Stop):b.charge(0)
        b=Budget();b.charge(20,count=0);self.assertEqual(b.methods,0)
        with self.assertRaises(Stop):b.charge(101)
        b=Budget(cpu=.001)
        with mock.patch('readonly_core.time.process_time',return_value=b.started_cpu+1):
            with self.assertRaisesRegex(Stop,'CPU'):b.resource_check()
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            e=Evidence(tmp,tmp,cap=100)
            with self.assertRaisesRegex(Stop,'DISK'):e.save('x',{'x':'x'})
        b=Budget(ram=1)
        with self.assertRaisesRegex(Stop,'RAM'):b.resource_check()

class State(unittest.TestCase):
    def test_oracle_strict_boundary_negative_future_and_fallback(self):
        rd=lambda a,u:(True,'0x'+b''.join(word(n) for n in [1,a,1,u,1]).hex())
        self.assertEqual(oracle_price(0,1,(3,60,8),rd(100,50),8,100),(10**12,'PRIMARY_FRESH_CHAINLINK'))
        for a,u in [(100,40),(0,50),(2**256-1,50),(100,101)]:
            with self.assertRaises(Stop):oracle_price(0,1,(3,60,8),rd(a,u),8,100)
        self.assertEqual(oracle_price(2,123,(3,60,8),(False,'0x'),8,100)[0],123)
        with self.assertRaises(Stop):oracle_price(1,1,(3,60,8),rd(100,50),8,100)
        with self.assertRaises(Stop):oracle_price(0,1,(3,60,8),(False,'0x'),8,100)
    def test_full_SP_zombie_fee_anchor_and_last_trove(self):
        r=lambda:{'id':1,'status':4,'latest':{'entireDebt':100*10**18,'entireColl':10**18}}
        policy={'method_review_accepted':True,'gas_limit':1000000,'priority_fee_wei':100000000}
        out=qualify([r()],2,11*10**17,101*10**18,10**18,0,policy,None)[0]
        self.assertTrue(out['eligible']);self.assertIsNone(out['fee_qualified'])
        out=qualify([r()],2,11*10**17,101*10**18,10**18,0,policy,2000*10**18)[0]
        self.assertTrue(out['fee_qualified']);self.assertEqual(out['attempt_cap_wei'],str(10**15))
        self.assertFalse(qualify([r()],1,11*10**17,101*10**18,10**18,0,policy,10**18)[0]['eligible'])
        self.assertFalse(qualify([r()],2,11*10**17,100*10**18,10**18,0,policy,10**18)[0]['eligible'])
    def test_episode_no_new_opportunity_from_gap_or_next_day(self):
        e=Episodes();r=lambda i,score:{'id':i,'eligible':True,'fee_qualified':True,'minimum_reward_minus_ceiling':score}
        self.assertEqual(e.update([r(2,10),r(1,10)],'day1','hash')['id'],1)
        self.assertIsNone(e.update([r(2,10),r(1,10)],'day2','hash2'))
        e.unknown();self.assertIsNone(e.update([r(2,20)],'day3','hash3'))
        e.update([{'id':2,'eligible':False}],'day3','hash3');self.assertEqual(e.update([r(2,20)],'day4','hash4')['id'],2)
    def test_reorg_correction_and_missing_gap(self):
        h=lambda n,b,p:{'number':hex(n),'hash':'0x'+b*64,'parentHash':'0x'+p*64}
        c=ChainTrack();self.assertEqual(c.accept(h(1,'1','0')),'FIRST');self.assertEqual(c.accept(h(2,'2','1')),'EXTENDS')
        self.assertEqual(c.accept(h(2,'3','1')),'REORG');self.assertEqual(c.headers[2]['hash'],'0x'+'3'*64)
        with self.assertRaisesRegex(Stop,'MISSING'):c.accept(h(4,'4','3'))
    def test_mixedblock_scanner_fence(self):
        class FakeBindings:
            addresses={'multicall':'0x'+'a'*40,'feed':'0x'+'2'*40,'sp':'0x'+'3'*40,'aggregator':'0x'+'4'*40}
            config={'fee_policy':{'method_review_accepted':False}};selectors={('multicall','aggregate3'):'0x82ad56cb'}
            def method(self,*a):return ('0x'+'1'*40,'0x12345678')
        enc=lambda *n:(True,'0x'+b''.join(word(v) for v in n).hex())
        first=[enc(2),enc(0),enc(11*10**17),enc(int('2'*40,16)),enc(int('3'*40,16)),enc(int('3'*40,16)),enc(0),enc(100),enc(int('4'*40,16),60,8),enc(1),enc(2)]
        second=[enc(1),enc(*([10**18]*10)),enc(4),enc(*([10**18]*10)),enc(1000*10**18),enc(10**18,0)]
        sc=Scanner(FakeBindings(),mock.Mock(),padding=2);sc.aggregate=mock.Mock(side_effect=[first,second]);sc.rpc.call.return_value={'number':'0x1','hash':'0x'+'f'*64}
        with self.assertRaisesRegex(Stop,'MIXED_BLOCK'):sc.snapshot({'number':'0x1','timestamp':hex(100),'hash':'0x'+'e'*64,'baseFeePerGas':'0x0'})
    def test_forecast_does_not_pass_over_quota(self):
        c={'rpc_CU':{'eth_call':26,'eth_getBlockByNumber':20,'eth_getLogs':60},'stream_notification_CU':20}
        with self.assertRaisesRegex(Stop,'QUOTA'):forecast(c,Budget(cu_limit=100),1,1,notification_bytes=[100])
        with self.assertRaisesRegex(Stop,'SCAN'):forecast(c,Budget(),1,13,notification_bytes=[100])

class NewSafetyAndEvidence(unittest.TestCase):
    def test_actual_notification_bytes_not_fixed_typical_value(self):
        c={'rpc_CU':{'eth_call':26,'eth_getBlockByNumber':20,'eth_getLogs':60}}
        with self.assertRaisesRegex(Stop,'ACTUAL_NOTIFICATION'):forecast(c,Budget(),1,1)
        # Synthetic 1k frame, labeled; this is NOT the actual provider size.
        with self.assertRaisesRegex(Stop,'QUOTA'):forecast(c,Budget(),1,1,notification_bytes=[1000])
        out=forecast(c,Budget(),1,1,notification_bytes=[100])
        self.assertEqual(out['conservative_stream_CU_per_head'],4)
    def test_delta_lossless_byte_ranges_and_periodic_full_baseline(self):
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            e=Evidence(tmp,tmp);last=None;expected=None
            for i in range(70):
                expected=json.dumps({'result':'0x'+('0'*4096)+str(i).zfill(12)})
                last=e.save('rpc',{'request':{'method':'eth_call','params':[{'input':'0x82ad56cb'}]},'body_utf8':expected})
            self.assertEqual(reconstruct_rpc_body(last,tmp).decode(),expected)
            self.assertLess(len(list(pathlib.Path(tmp).glob('*.gz'))),5)
            self.assertEqual(len(read_artifact_range(last)),last['bytes'])
    def test_WS_notification_charge_by_actual_payload_and_frame(self):
        payload=json.dumps({'method':'eth_subscription','params':{'subscription':'s','result':{'x':'x'*300}}}).encode()
        wire=b'\x81\x7e'+len(payload).to_bytes(2,'big')+payload
        class Sock:
            def __init__(self,b):self.b=b
            def recv(self,n):x=self.b[:n];self.b=self.b[n:];return x
        h=HeadStream.__new__(HeadStream);h.sock=Sock(wire);h.max_body=10000;h.budget=Budget();h.endpoint=SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/fixture');h.evidence=mock.Mock();h.notification_payload_bytes=[];h.notification_wire_bytes=[]
        self.assertEqual(h.receive_json()['method'],'eth_subscription')
        self.assertEqual(h.budget.methods,0)
        self.assertEqual(h.budget.cu,(len(payload)+4+24)//25)
        self.assertEqual(h.notification_payload_bytes,[len(payload)])
        with self.assertRaisesRegex(Stop,'DISCONNECTED'):h.receive_json()
    def test_real_dependency_ABIs_and_runtime_records_decode_static(self):
        from readonly_collector import Bindings,HERE
        b=Bindings(HERE/'bindings.json')
        self.assertEqual(set(b.records),{'tm','sp','feed','registry','multicall'})
        self.assertEqual(b.selectors[('feed','fetchPrice')],'0x0fdb11cf')
        self.assertEqual(b.selectors[('sp','getTotalBoldDeposits')],'0xf71c6940')
        self.assertTrue(all(len(x)>2 for x in b.runtime.values()))
    def test_missing_release_stops_before_secret_prompt(self):
        import readonly_collector as c
        with mock.patch.object(c,'verify_release',side_effect=Stop('STATIC_RELEASE_MISSING')):
            with mock.patch.object(c,'prompt_endpoint') as prompt:
                with self.assertRaisesRegex(Stop,'STATIC_RELEASE_MISSING'):c.load_admission(c.HERE/'bindings.json')
                prompt.assert_not_called()

class DeadlineReleaseAndFeed(unittest.TestCase):
    def test_expired_preflight_never_prompts_secret(self):
        import readonly_collector as c
        with mock.patch.object(c.time,'time',return_value=1792470001):
            with mock.patch.object(c,'prompt_endpoint') as prompt:
                with self.assertRaisesRegex(Stop,'DEADLINE'):c.run_live(c.HERE/'bindings.json')
                prompt.assert_not_called()
    def test_code_hash_release_drift_rejected(self):
        import readonly_collector as c
        with tempfile.TemporaryDirectory(dir=c.HERE) as tmp:
            root=pathlib.Path(tmp);(root/'root').mkdir()
            code={p.name:digest(p.read_bytes()) for p in [c.HERE/'readonly_core.py',c.HERE/'readonly_collector.py',c.HERE/'start-A-local.command']};code['readonly_core.py']='0'*64
            (root/'root/live-preflight-release.json').write_text(json.dumps({'status':'RELEASED_READONLY_A_PREFLIGHT','bindings_sha256':digest(b'{}'),'reviewed_code_sha256':code}))
            binding=mock.Mock();binding.raw=b'{}'
            with mock.patch.object(c,'UNIT',root):
                with self.assertRaisesRegex(Stop,'CODE_HASH'):c.verify_release(binding)
    def test_feed_newfailure_is_policy_unknown_and_fetch_is_last(self):
        class FB:
            addresses={'multicall':'0x'+'a'*40,'feed':'0x'+'2'*40,'sp':'0x'+'3'*40};config={'fee_policy':{'method_review_accepted':False}}
            def method(self,*args):return args
        enc=lambda *n:(True,'0x'+b''.join(word(v) for v in n).hex())
        first=[enc(2),enc(0),enc(11*10**17),enc(int('2'*40,16)),enc(int('3'*40,16)),enc(int('3'*40,16)),enc(0),enc(100),enc(int('4'*40,16),60,8),enc(1),enc(2)]
        second=[enc(1),enc(*([10**18]*10)),enc(4),enc(*([10**18]*10)),enc(1000*10**18),enc(100,1)]
        rpc=mock.Mock();rpc.call.return_value={'number':'0x1','hash':'0x'+'e'*64};sc=Scanner(FB(),rpc,padding=2);sc.aggregate=mock.Mock(side_effect=[first,second]);head={'number':'0x1','timestamp':hex(100),'hash':'0x'+'e'*64,'baseFeePerGas':'0x0'}
        snapshot=sc.snapshot(head)
        self.assertTrue(snapshot['oracle_raw']['simulated_newOracleFailureDetected']);self.assertIsNone(snapshot['rows'][0]['eligible'])
        self.assertEqual(sc.aggregate.call_args_list[1].args[0][-1],('feed','fetchPrice'))
        second[-1]=(False,'0x');sc.aggregate=mock.Mock(side_effect=[first,second])
        with self.assertRaisesRegex(Stop,'FETCH_PRICE_REVERT'):sc.snapshot(head)

if __name__=='__main__':unittest.main(verbosity=2)
