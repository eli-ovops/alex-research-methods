"""Synthetic SAFETY tests only: no real error reproduction, network or credential."""
import unittest,unittest.mock as mock,tempfile,pathlib,gzip,json,errno
import candidate_readonly_core as c

FAKE='PSEUDO_SECRET_ONLY_FOR_SAFETY'

class SafeDiagnostic(unittest.TestCase):
    def setUp(self):
        self.block=mock.patch.object(c.socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN_OFFLINE'));self.block.start();self.addCleanup(self.block.stop)
    def check_record(self,phase,ex,reading=False,build=False):
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            e=c.Evidence(tmp,tmp);r=c.RPC(c.SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/'+FAKE),c.Budget(),e,{'eth_chainId':0});r.opener=mock.Mock()
            class Response:
                code=200;headers={}
                def __init__(self):self.n=0
                def __enter__(self):return self
                def __exit__(self,*a):pass
                def read(self,n):
                    self.n+=1
                    if self.n==1:return FAKE.encode()
                    raise ex
            if reading:r.opener.open.return_value=Response()
            else:r.opener.open.side_effect=ex
            patch=mock.patch.object(c.urllib.request,'Request',side_effect=ex) if build else mock.patch.object(c,'utc',wraps=c.utc)
            with patch:
                with self.assertRaises(c.Stop) as stopped:r.call('eth_chainId',[])
            text=b''.join(gzip.decompress(p.read_bytes()) for p in pathlib.Path(tmp).glob('*.gz'))
            self.assertNotIn(FAKE.encode(),text);self.assertNotIn(FAKE,str(stopped.exception));self.assertNotIn(b'body_utf8',text)
            row=json.loads(text);self.assertFalse(row['provider_error_body_saved']);diag=row['transport_diagnostic'];self.assertEqual(diag['phase'],phase)
            self.assertEqual(type(diag['elapsed_monotonic_ns']),int);self.assertEqual(type(diag['bytes_received']),int)
            self.assertEqual(r.opener.open.call_count,0 if build else 1)
            return row
    def test_open_URLError_reason_text_not_saved(self):
        d=self.check_record('OPEN',c.urllib.error.URLError(FAKE))['transport_diagnostic']
        self.assertEqual(d['exception_type'],'URLError');self.assertEqual(d['reason_type'],'TEXT_NOT_SAVED');self.assertIsNone(d['errno']);self.assertEqual(d['bytes_received'],0)
    def test_read_nested_errno_and_partial_bytes(self):
        d=self.check_record('READ',c.urllib.error.URLError(ConnectionResetError(errno.ECONNRESET,FAKE)),reading=True)['transport_diagnostic']
        self.assertEqual(d['reason_type'],'ConnectionResetError');self.assertEqual(d['errno'],errno.ECONNRESET);self.assertEqual(d['bytes_received'],len(FAKE))
    def test_request_build_phase(self):
        d=self.check_record('REQUEST_BUILD',ValueError(FAKE),build=True)['transport_diagnostic'];self.assertEqual(d['exception_type'],'ValueError')
    def test_unknown_dynamic_class_and_nested_class_name_not_saved(self):
        def forbidden_str(self):raise AssertionError('EXCEPTION_TEXT_WAS_READ')
        Custom=type(FAKE,(Exception,),{'__str__':forbidden_str,'__repr__':forbidden_str})
        d=self.check_record('OPEN',Custom(FAKE))['transport_diagnostic'];self.assertEqual(d['exception_type'],'OTHER')
        d=self.check_record('OPEN',c.urllib.error.URLError(Custom(FAKE)))['transport_diagnostic'];self.assertEqual(d['reason_type'],'OTHER')
    def test_TLS_flags_and_integer_only_fields(self):
        ex=c.ssl.SSLCertVerificationError(FAKE);ex.verify_code=42;ex.errno=True
        d=c.safe_transport_diagnostic(c.urllib.error.URLError(ex),'OPEN',c.time.monotonic_ns(),0)
        self.assertTrue(d['TLS']);self.assertTrue(d['certificate_verification']);self.assertEqual(d['verify_code'],42);self.assertIsNone(d['errno'])
        ex.verify_code=FAKE;ex.errno=FAKE;d=c.safe_transport_diagnostic(ex,'READ',c.time.monotonic_ns(),1)
        self.assertIsNone(d['verify_code']);self.assertIsNone(d['errno']);self.assertNotIn(FAKE,json.dumps(d))
    def test_timeout_and_invalid_phase_types(self):
        d=c.safe_transport_diagnostic(c.urllib.error.URLError(TimeoutError(FAKE)),FAKE,c.time.monotonic_ns(),True)
        self.assertTrue(d['timeout']);self.assertEqual(d['phase'],'OTHER');self.assertEqual(d['bytes_received'],0);self.assertNotIn(FAKE,json.dumps(d))
    def test_HTTP_refusal_still_stops_without_diagnostic_or_body(self):
        class Response:
            code=403;headers={}
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,n):return b''
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            r=c.RPC(c.SecretEndpoint('https://eth-mainnet.g.alchemy.com/v2/'+FAKE),c.Budget(),c.Evidence(tmp,tmp),{'eth_chainId':0});r.opener=mock.Mock();r.opener.open.return_value=Response()
            with self.assertRaisesRegex(c.Stop,'HTTP_REFUSAL_OR_ERROR_403'):r.call('eth_chainId',[])
            row=json.loads(b''.join(gzip.decompress(p.read_bytes()) for p in pathlib.Path(tmp).glob('*.gz')));self.assertNotIn('transport_diagnostic',row);self.assertNotIn('body_utf8',row);self.assertEqual(r.opener.open.call_count,1)

if __name__=='__main__':unittest.main(verbosity=2)
