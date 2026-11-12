#!/usr/bin/env python3
"""Separate, Root-gated format/literal availability question; never emits log text."""
import datetime as dt,hashlib,json,os,pathlib,re,resource,stat,time
HERE=pathlib.Path(__file__).resolve().parent
UNIT=HERE.parents[1]
LOG=pathlib.Path('/Users/USER/Library/Logs/ClashFX/com.clashfx.app 2026-10-20--19-12-31-899-+0800.log')
MAX_BYTES=1048576
MAX_LINE=16384
HOST=b'eth-mainnet.g.alchemy.com'
FORMATS=('DATE_DASH_SPACE','DATE_DASH_T','DATE_SLASH_SPACE','CLOCK_ONLY','OTHER')
# Exact syntactic categories. Optional . , or : fractional digits; offset/Z accepted only at suffix boundary.
SUFFIX=rb'(?:[.,:](\d{1,9}))?\s*(Z|[+-]\d{2}:?\d{2})?(?=\]|\s|$)'
PATTERNS=(
 ('DATE_DASH_SPACE',re.compile(rb'^\s*\[?(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})'+SUFFIX)),
 ('DATE_DASH_T',re.compile(rb'^\s*\[?(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})'+SUFFIX)),
 ('DATE_SLASH_SPACE',re.compile(rb'^\s*\[?(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})'+SUFFIX)),
 ('CLOCK_ONLY',re.compile(rb'^\s*\[?(\d{2}):(\d{2}):(\d{2})'+SUFFIX)),
)
ERROR_WORDS={'TIMEOUT':(b'TimeoutError',b'timeout',b'timed out'),'TLS_EOF':(b'SSLEOFError',),'CERT_VERIFY':(b'SSLCertVerificationError',b'CERTIFICATE_VERIFY_FAILED'),'CONNECTION_REFUSED':(b'ConnectionRefusedError',),'CONNECTION_RESET':(b'ConnectionResetError',)}
class SafeStop(Exception):pass

def released():
    p=UNIT/'root/ClashFX-format-host-classifier-release.json'
    if not p.is_file():raise SafeStop('RELEASE_MISSING')
    r=json.loads(p.read_bytes())
    if r.get('status')!='RELEASED_SINGLE_FIXED_LOG_FORMAT_HOST_CLASSIFIER' or r.get('script_sha256')!=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest():raise SafeStop('RELEASE_IDENTITY')
    expected={'log_path':str(LOG),'max_prefix_bytes':MAX_BYTES,'max_line_bytes':MAX_LINE,'question':'FORMAT_AND_LITERAL_HOST_AVAILABILITY_ONLY','conditional_window_Beijing':['2026-10-20T19:30:08+08:00','2026-10-20T19:30:18+08:00']}
    if any(r.get(k)!=v for k,v in expected.items()):raise SafeStop('RELEASE_SCOPE')
    if dt.datetime.now(dt.timezone.utc)>=dt.datetime.fromisoformat(r['valid_until_UTC'].replace('Z','+00:00')):raise SafeStop('RELEASE_EXPIRED')

def classify(line):
    for name,pattern in PATTERNS:
        m=pattern.match(line)
        if not m:continue
        g=m.groups();zone=g[-1];fraction=g[-2]
        # Only digit groups are converted. Full log lines, URL/path/auth values are never decoded.
        try:
            if name=='CLOCK_ONLY':
                hh,mm,ss=map(int,g[:3]);dt.time(hh,mm,ss);full=None
            else:full=dt.datetime(*map(int,g[:6]))
            if zone is not None and zone!=b'Z':
                v=zone[1:].replace(b':',b'');hours,minutes=int(v[:2]),int(v[2:])
                if hours>23 or minutes>59:return 'OTHER',False,None
        except (ValueError,OverflowError):return 'OTHER',False,None
        return name,zone is not None,full
    return 'OTHER',False,None

def main():
    released()  # No log target access before exact new release. Old release is never consulted.
    with (HERE/'format-host-classifier.once.lock').open('x') as f:f.write('ONE_SEPARATE_FORMAT_HOST_QUESTION\n')
    started=time.process_time();fd=None
    result={'status':'INCONCLUSIVE_LOCAL','UTC_acquisition_started':dt.datetime.now(dt.timezone.utc).isoformat(),'format_counts':{k:{'zone_present':0,'zone_absent':0} for k in FORMATS},'complete_bounded_lines':0,'literal_fixed_host_line_count':0,'overlong_line_count':0,'trailing_incomplete_line_count':0,'CONDITIONAL_UNVERIFIED_TIMEZONE':{'assumption':'Interpret recognized full date with no explicit zone as Beijing only; not actual verified time','target_date':'2026-10-20','seconds_inclusive':'19:30:08–19:30:17','recognized_full_date_zone_absent_line_count':0,'window_line_count':0,'window_host_literal_line_count':0,'window_host_error_word_counts':{k:0 for k in [*ERROR_WORDS,'UNKNOWN']}},'no_actual_timezone_or_connection_or_cause_claim':True,'no_raw_text_or_arbitrary_values_saved':True}
    try:
        fd=os.open(LOG,os.O_RDONLY|os.O_NOFOLLOW);before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):raise SafeStop('NOT_REGULAR_FILE')
        if not 0<=before.st_size<=MAX_BYTES:raise SafeStop('INITIAL_FILE_SIZE_LIMIT')
        initial=before.st_size;data=bytearray()
        while len(data)<initial:
            b=os.read(fd,min(65536,initial-len(data)))
            if not b:raise SafeStop('PREFIX_SHORT_READ')
            data.extend(b)
        after=os.fstat(fd);current=LOG.lstat();stable=before.st_dev==after.st_dev==current.st_dev and before.st_ino==after.st_ino==current.st_ino and stat.S_ISREG(current.st_mode) and after.st_size>=initial
        result.update(prefix_literal_fixed_host_occurrence_count=data.count(HOST),initial_size_bytes=initial,prefix_bytes_read=len(data),prefix_sha256=hashlib.sha256(data).hexdigest(),inode_path_identity_stable=stable,file_may_append=after.st_size>initial,whole_file_immutable_or_atomic_claim=False)
        if not stable:raise SafeStop('FILE_IDENTITY_CHANGED')
        pos=0
        while pos<len(data):
            end=data.find(b'\n',pos)
            if end<0:result['trailing_incomplete_line_count']+=1;break
            length=end-pos;nextpos=end+1
            if length>MAX_LINE:result['overlong_line_count']+=1;pos=nextpos;continue
            line=bytes(data[pos:end]).rstrip(b'\r');pos=nextpos
            if not line.strip():continue
            result['complete_bounded_lines']+=1;host=HOST in line
            if host:result['literal_fixed_host_line_count']+=1
            fmt,zone,full=classify(line);result['format_counts'][fmt]['zone_present' if zone else 'zone_absent']+=1
            if full is None or zone:continue
            conditional=result['CONDITIONAL_UNVERIFIED_TIMEZONE'];conditional['recognized_full_date_zone_absent_line_count']+=1
            if full.date()!=dt.date(2026,10,20) or not dt.time(19,30,8)<=full.time()<dt.time(19,30,18):continue
            conditional['window_line_count']+=1
            if not host:continue
            conditional['window_host_literal_line_count']+=1
            labels=[k for k,tokens in ERROR_WORDS.items() if any(token in line for token in tokens)] or ['UNKNOWN']
            for label in labels:conditional['window_host_error_word_counts'][label]+=1
        result['status']='ONE_BOUNDED_FORMAT_LITERAL_PROJECTION_ONLY'
    except BaseException as ex:
        allowed={'NOT_REGULAR_FILE','INITIAL_FILE_SIZE_LIMIT','PREFIX_SHORT_READ','FILE_IDENTITY_CHANGED'}
        result['safe_stop_code']=ex.args[0] if type(ex)is SafeStop and len(ex.args)==1 and ex.args[0] in allowed else 'LOCAL_SAFE_FAILURE'
    finally:
        if fd is not None:os.close(fd)
        result.update(UTC_acquisition_ended=dt.datetime.now(dt.timezone.utc).isoformat(),process_body_CPU_seconds=time.process_time()-started,maxrss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        with (HERE/'format-host-classifier-result.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
        print(result['status'])
    return 0 if result['status']=='ONE_BOUNDED_FORMAT_LITERAL_PROJECTION_ONLY' else 2

if __name__=='__main__':
    try:code=main()
    except BaseException:print('STOPPED_LOCAL_SAFE_GUARD');code=2
    raise SystemExit(code)
