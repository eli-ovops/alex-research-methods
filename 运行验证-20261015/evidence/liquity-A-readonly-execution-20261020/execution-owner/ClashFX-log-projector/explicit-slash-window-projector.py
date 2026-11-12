#!/usr/bin/env python3
"""Root-release-gated, one-file in-memory projection. Never emits log text."""
import datetime as dt, hashlib, json, os, pathlib, re, resource, stat, time
HERE=pathlib.Path(__file__).resolve().parent
UNIT=HERE.parents[1]
LOG=pathlib.Path('/Users/USER/Library/Logs/ClashFX/com.clashfx.app 2026-10-20--19-12-31-899-+0800.log')
MAX_BYTES=1048576
EXPECTED_PREFIX_BYTES=906378
EXPECTED_PREFIX_SHA256='675e27a1473975ec7535cacc0c7b870a36f5d425573dfd8876de6e50a3a5306d'
MAX_LINE=16384
HOST=b'eth-mainnet.g.alchemy.com'
BEIJING=dt.timezone(dt.timedelta(hours=8))
START=dt.datetime(2026,10,20,19,30,8,tzinfo=BEIJING)
END=dt.datetime(2026,10,20,19,30,18,tzinfo=BEIJING)  # seconds08 through17 inclusive
# Prefix only. Offset/Z is mandatory; filename timezone and local OS timezone are never inferred.
TIMESTAMP=re.compile(rb'^\s*\[?(\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2})(T| )(\d{2}:\d{2}:\d{2})(?:[.,:](\d{1,9}))?\s*(Z|[+-]\d{2}:?\d{2})(?=\]|\s|$)')
PHASE_WORDS={'SOCKET_CONNECT':(b'SOCKET_CONNECT',),'PROXY_CONNECT_SEND':(b'PROXY_CONNECT_SEND',),'PROXY_CONNECT_HEADER':(b'PROXY_CONNECT_HEADER',),'TLS_HANDSHAKE':(b'TLS_HANDSHAKE',b'TLS handshake'),'HTTP_REQUEST_SEND':(b'HTTP_REQUEST_SEND',),'HTTP_RESPONSE_HEADER':(b'HTTP_RESPONSE_HEADER',)}
ERROR_WORDS={'TIMEOUT':(b'TimeoutError',b'timeout',b'timed out'),'TLS_EOF':(b'SSLEOFError',),'CERT_VERIFY':(b'SSLCertVerificationError',b'CERTIFICATE_VERIFY_FAILED'),'CONNECTION_REFUSED':(b'ConnectionRefusedError',),'CONNECTION_RESET':(b'ConnectionResetError',)}
MARKER_WORDS={k:k.encode('ascii') for k in ('tls','timeout','dial','tcp','udp','match','connect','proxy','connection_refused','connection_reset','eof')}
class SafeStop(Exception):pass

def released():
    p=UNIT/'root/ClashFX-explicit-slash-window-projector-release.json'
    if not p.is_file():raise SafeStop('RELEASE_MISSING')
    r=json.loads(p.read_bytes())
    if r.get('status')!='RELEASED_EXACT_PREFIX_EXPLICIT_SLASH_WINDOW_PROJECTOR' or r.get('script_sha256')!=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest():raise SafeStop('RELEASE_IDENTITY')
    if r.get('log_path')!=str(LOG) or r.get('max_prefix_bytes')!=MAX_BYTES or r.get('exact_prefix_bytes')!=EXPECTED_PREFIX_BYTES or r.get('expected_prefix_sha256')!=EXPECTED_PREFIX_SHA256 or r.get('max_line_bytes')!=MAX_LINE or r.get('window_Beijing')!=['2026-10-20T19:30:08+08:00','2026-10-20T19:30:18+08:00']:raise SafeStop('RELEASE_SCOPE')
    if dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(r['valid_until_UTC'].replace('Z','+00:00')):raise SafeStop('RELEASE_EXPIRED')

def classify(line,words):
    # Counts literal lexical labels only, never extracts a substring or arbitrary error value.
    found=[label for label,tokens in words.items() if any(token in line for token in tokens)]
    return found or ['UNKNOWN']

def parse_time(line):
    m=TIMESTAMP.match(line)
    if not m:return None,None
    date,sep,clock,fraction,offset=m.groups()
    offset=offset.decode('ascii')
    if offset=='Z':zone=dt.timezone.utc
    else:
        val=offset[1:].replace(':','');hours=int(val[:2]);minutes=int(val[2:])
        if hours>23 or minutes>59:return None,None
        zone=dt.timezone(dt.timedelta(minutes=(hours*60+minutes)*(1 if offset[0]=='+' else -1)))
    try:value=dt.datetime.strptime((date.replace(b'/',b'-')+b' '+clock).decode('ascii'),'%Y-%m-%d %H:%M:%S').replace(tzinfo=zone,microsecond=int((fraction or b'').ljust(6,b'0')[:6]))
    except (ValueError,OverflowError):return None,None
    # Window boundaries are exact whole seconds; any fraction within seconds08..17 is inside.
    local=value.astimezone(BEIJING)
    inside=START.replace(microsecond=0)<=local.replace(microsecond=0)<END
    return (local,inside),('DATE_SLASH_' if b'/' in date else 'DATE_DASH_')+('T_EXPLICIT_ZONE' if sep==b'T' else 'SPACE_EXPLICIT_ZONE')

def main():
    released()  # No target log stat/open before exact Root publication.
    with (HERE/'explicit-slash-window.once.lock').open('x') as f:f.write('ONE_EXACT_PREFIX_EXPLICIT_SLASH_PROJECTION_NO_NETWORK\n')
    start=time.process_time();fd=None
    result={'status':'INCONCLUSIVE','UTC_acquisition_started':dt.datetime.now(dt.timezone.utc).isoformat(),'target_date_Beijing':'2026-10-20','window_Beijing_seconds_inclusive':'19:30:08–19:30:17','explicit_time_format_counts':{k:0 for k in ('DATE_DASH_T_EXPLICIT_ZONE','DATE_DASH_SPACE_EXPLICIT_ZONE','DATE_SLASH_T_EXPLICIT_ZONE','DATE_SLASH_SPACE_EXPLICIT_ZONE')},'target_date_identified_line_count':0,'window_identified_line_count':0,'window_fixed_host_line_count':0,'phase_label_counts':{k:0 for k in [*PHASE_WORDS,'UNKNOWN']},'error_label_counts':{k:0 for k in [*ERROR_WORDS,'UNKNOWN']},'window_host_ASCII_marker_counts':{k:0 for k in [*MARKER_WORDS,'UNKNOWN']},'overlong_line_count':0,'unknown_time_line_count':0,'trailing_incomplete_line_count':0,'original_log_text_saved_or_output':False,'lexical_counts_not_causal_classification':True}
    try:
        fd=os.open(LOG,os.O_RDONLY|os.O_NOFOLLOW)
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):raise SafeStop('NOT_REGULAR_FILE')
        if not 0<EXPECTED_PREFIX_BYTES<=MAX_BYTES:raise SafeStop('FIXED_PREFIX_SIZE_LIMIT')
        if before.st_size<EXPECTED_PREFIX_BYTES:raise SafeStop('FILE_SHORTER_THAN_FIXED_PREFIX')
        size=EXPECTED_PREFIX_BYTES;data=bytearray()
        while len(data)<size:
            chunk=os.read(fd,min(65536,size-len(data)))
            if not chunk:raise SafeStop('PREFIX_SHORT_READ')
            data.extend(chunk)
        after=os.fstat(fd);current=LOG.lstat()
        stable=before.st_dev==after.st_dev==current.st_dev and before.st_ino==after.st_ino==current.st_ino and stat.S_ISREG(current.st_mode) and after.st_size>=size
        result.update(initial_file_size_bytes=before.st_size,exact_prefix_size_bytes=size,prefix_bytes_read=len(data),prefix_sha256=hashlib.sha256(data).hexdigest(),inode_path_identity_stable=stable,file_may_append=after.st_size>before.st_size,whole_file_immutable_claim=False)
        if not stable:raise SafeStop('FILE_IDENTITY_CHANGED')
        if result['prefix_sha256']!=EXPECTED_PREFIX_SHA256:raise SafeStop('FIXED_PREFIX_HASH_MISMATCH')
        result['fixed_prefix_hash_matched']=True
        # Bound each processed line; never decode a whole log line or URL/auth/subscription field.
        pos=0
        while pos<len(data):
            end=data.find(b'\n',pos)
            if end<0:
                result['trailing_incomplete_line_count']+=1;break
            length=end-pos;nextpos=end+1
            if length>MAX_LINE:result['overlong_line_count']+=1;pos=nextpos;continue
            line=bytes(data[pos:end]).rstrip(b'\r');pos=nextpos
            if not line.strip():continue
            parsed,fmt=parse_time(line)
            if parsed is None:result['unknown_time_line_count']+=1;continue
            result['explicit_time_format_counts'][fmt]+=1;local,inside=parsed
            if local.date()!=START.date():continue
            result['target_date_identified_line_count']+=1
            if not inside:continue
            result['window_identified_line_count']+=1
            if HOST not in line:continue
            result['window_fixed_host_line_count']+=1
            for k in classify(line,PHASE_WORDS):result['phase_label_counts'][k]+=1
            for k in classify(line,ERROR_WORDS):result['error_label_counts'][k]+=1
            lowered=line.lower();markers=[k for k,token in MARKER_WORDS.items() if token in lowered] or ['UNKNOWN']
            for k in markers:result['window_host_ASCII_marker_counts'][k]+=1
        complete=any(result['explicit_time_format_counts'].values()) and not result['unknown_time_line_count'] and not result['overlong_line_count'] and not result['trailing_incomplete_line_count']
        result['status']='COMPLETE_BOUNDED_PREFIX_PROJECTION_NOT_LOG_COMPLETENESS_PROOF' if complete else 'INCONCLUSIVE_FORMAT_OR_TIME_COVERAGE'
    except BaseException as ex:
        allowed={'NOT_REGULAR_FILE','FIXED_PREFIX_SIZE_LIMIT','FILE_SHORTER_THAN_FIXED_PREFIX','PREFIX_SHORT_READ','FILE_IDENTITY_CHANGED','FIXED_PREFIX_HASH_MISMATCH'}
        result['safe_stop_code']=ex.args[0] if type(ex)is SafeStop and len(ex.args)==1 and ex.args[0] in allowed else 'LOCAL_SAFE_FAILURE'
    finally:
        if fd is not None:os.close(fd)
        result.update(UTC_acquisition_ended=dt.datetime.now(dt.timezone.utc).isoformat(),process_body_CPU_seconds=time.process_time()-start,maxrss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        with (HERE/'explicit-slash-window-result.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
        print(result['status'])
    return 0 if result['status'].startswith('COMPLETE_BOUNDED') else 2

if __name__=='__main__':
    try:code=main()
    except BaseException:print('STOPPED_LOCAL_SAFE_GUARD');code=2
    raise SystemExit(code)
