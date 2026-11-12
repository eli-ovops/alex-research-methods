import sys, os, time, json, hashlib, base64, resource, csv, urllib.request, urllib.error
from pathlib import Path
from decimal import Decimal, InvalidOperation
from collections import Counter, defaultdict
from datetime import datetime, timezone

P = Path(__file__).resolve().parent
START = json.loads((P / "start.json").read_text())
T0 = START["monotonic"]
EXPECTED = 394775342
MAX_RSS = 256 * 1024**2
MAX_DISK = int(.5 * 1024**3)
URL = "https://www.kaggle.com/api/v1/datasets/download/mczielinski/bitcoin-historical-data/btcusd_1-min_data.csv?datasetVersionNumber=755"
ETAG = '"f86437a73b9cab3538b678e0b395dd5b"'
GEN = "1792203034562955"
DOWNLOAD = P / "btcusd_1-min_data.csv.partial"
ST = {"status": "STARTED", "download_complete": False, "scan_complete": False}
def now(): return datetime.now(timezone.utc).isoformat()
def dump(n, v): (P/n).write_text(json.dumps(v, indent=2, ensure_ascii=False)+"\n")
def rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == "darwin" else r*1024)
def limits():
    if time.monotonic()-T0 > 900: raise RuntimeError("WALL_TIME_LIMIT")
    if rss() > MAX_RSS: raise RuntimeError("RSS_LIMIT")
    if sum(f.stat().st_size for f in P.iterdir() if f.is_file()) > MAX_DISK: raise RuntimeError("DISK_LIMIT")
def checkpoint():
    ST["wall_seconds"] = time.monotonic()-T0
    ST["peak_RSS_bytes"] = rss()
    dump("progress.json", ST)

try:
    if DOWNLOAD.exists(): raise RuntimeError("NO_OVERWRITE_NO_RETRY")
    limits()
    req = urllib.request.Request(URL, headers={"If-Match": ETAG})
    receipt = {"url": URL, "request_If_Match": ETAG, "start_utc": now(), "auth_cookie_sent": False}
    try: response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e: response = e
    with response as r:
        h = {k:("[REDACTED response session]" if k.lower()=="set-cookie" else v) for k,v in r.headers.items()}
        lower = {k.lower():v for k,v in h.items()}
        receipt.update({"status": r.status, "headers": h, "final_domain": urllib.parse.urlparse(r.url).hostname})
        dump("download.receipt.json", receipt)
        if r.status != 200: raise RuntimeError("NON_200_STOP")
        if lower.get("etag") != ETAG or lower.get("x-goog-generation") != GEN: raise RuntimeError("OBJECT_IDENTITY_CHANGED")
        if int(lower.get("content-length", "-1")) != EXPECTED: raise RuntimeError("CONTENT_LENGTH_MISMATCH")
        sha, md5 = hashlib.sha256(), hashlib.md5()
        count = 0
        with DOWNLOAD.open("xb") as f:
            while True:
                limits()
                chunk = r.read(min(1024*1024, EXPECTED+1-count))
                if not chunk: break
                count += len(chunk); f.write(chunk); sha.update(chunk); md5.update(chunk)
                if count > EXPECTED: raise RuntimeError("BODY_EXCEEDS_EXPECTED")
        receipt.update({"end_utc": now(), "bytes": count, "sha256": sha.hexdigest(),
                        "md5_hex": md5.hexdigest(), "md5_base64": base64.b64encode(md5.digest()).decode()})
        hashes = lower.get("x-goog-hash","")
        server_md5 = next((part.strip()[4:] for part in hashes.split(",") if part.strip().startswith("md5=")), None)
        receipt["server_md5_base64"] = server_md5
        receipt["md5_matches_server"] = receipt["md5_base64"] == server_md5
        dump("download.receipt.json", receipt)
        if count != EXPECTED: raise RuntimeError("SHORT_BODY")
        if not receipt["md5_matches_server"]: raise RuntimeError("MD5_MISMATCH")
    final = P/"btcusd_1-min_data.csv"
    if final.exists(): raise RuntimeError("DESTINATION_EXISTS")
    DOWNLOAD.rename(final)
    ST["download_complete"] = True
    ST["downloaded_bytes"] = count
    checkpoint()
    print("DOWNLOAD_COMPLETE", count, sha.hexdigest(), flush=True)

    counters = Counter()
    field_parse, field_nonfinite = Counter(), Counter()
    examples = defaultdict(list)
    days, gap_distribution = Counter(), Counter()
    expected_header = ["Timestamp","Open","High","Low","Close","Volume"]
    previous = None; first = None; last = None; first_row = None; last_row = None
    inferred_missing = 0; strictly_increasing = True
    def error(kind, rownum, row, detail=None):
        counters[kind] += 1
        if len(examples[kind]) < 10: examples[kind].append({"data_row":rownum,"values":row,"detail":detail})
    scan_start = now()
    with final.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != expected_header: raise RuntimeError("HEADER_MISMATCH")
        for n, row in enumerate(reader,1):
            counters["rows_total"] += 1
            if first_row is None: first_row = row
            last_row = row
            if n%10000==0: limits()
            if n%500000==0:
                ST["rows_scanned"] = n; checkpoint(); print("SCANNED",n,flush=True)
            if len(row)!=6:
                error("wrong_width",n,row); continue
            vals=[]; valid=True
            for k, x in zip(header,row):
                if not x.strip(): counters["empty_values"] += 1
                try: v=Decimal(x)
                except InvalidOperation:
                    field_parse[k]+=1; error("parse_errors",n,row,k); valid=False; vals.append(None); continue
                vals.append(v)
                if not v.is_finite():
                    field_nonfinite[k]+=1; error("nonfinite_values",n,row,k); valid=False
            ts=vals[0]
            if ts is not None and ts.is_finite():
                if ts != ts.to_integral_value():
                    error("timestamp_noninteger",n,row)
                else:
                    t=int(ts)
                    if t%60: error("timestamp_off_minute_grid",n,row)
                    try: date=datetime.fromtimestamp(t,timezone.utc).date().isoformat(); days[date]+=1
                    except (ValueError,OverflowError,OSError): error("timestamp_out_of_datetime_range",n,row)
                    if first is None: first=t
                    last=t
                    if previous is not None:
                        delta=t-previous; gap_distribution[str(delta)]+=1
                        if delta<=0:
                            strictly_increasing=False
                            error("nonincreasing_timestamp",n,row,delta)
                            if delta==0: counters["adjacent_duplicate_timestamp"]+=1
                        elif delta!=60:
                            error("non60_interval",n,row,delta)
                            if delta%60==0: inferred_missing += delta//60-1
                            else: counters["positive_nonmultiple60_interval"]+=1
                    previous=t
            if not valid: continue
            _,o,h,l,c,v=vals
            if any(x<=0 for x in [o,h,l,c]): error("nonpositive_price_rows",n,row)
            if v<0: error("negative_volume_rows",n,row)
            elif v==0: counters["zero_volume_rows"]+=1
            else: counters["positive_volume_rows"]+=1
            if h<max(o,c,l): error("high_violation",n,row)
            if l>min(o,c,h): error("low_violation",n,row)
    limits()
    with final.open("rb") as f:
        f.seek(-1,2); last_newline=f.read()==b"\n"
    day_csv=P/"UTC-label-date-row-counts.csv"
    with day_csv.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["UTC_label_date","row_count"])
        w.writerows(sorted(days.items()))
    details = {"status":"COMPLETE_STATIC_SCAN", "scan_start_utc":scan_start,"scan_end_utc":now(),
        "header":header,"data_rows":counters["rows_total"],"first_row":first_row,"last_row":last_row,
        "first_timestamp_seconds":first,"last_timestamp_seconds":last,
        "first_label_UTC":datetime.fromtimestamp(first,timezone.utc).isoformat() if first is not None else None,
        "last_label_UTC":datetime.fromtimestamp(last,timezone.utc).isoformat() if last is not None else None,
        "counters":dict(counters),"field_parse_errors":dict(field_parse),"field_nonfinite":dict(field_nonfinite),
        "examples_max10_per_class":dict(examples),"adjacent_delta_distribution_seconds":dict(gap_distribution),
        "strictly_increasing_all_parsed_integer_timestamps":strictly_increasing,
        "global_duplicate_inference":"NONE if every row has valid integer timestamp and strict increase; otherwise UNKNOWN",
        "minute_grid_inferred_missing_rows":inferred_missing,
        "missing_grid_assumption":"Sum(delta/60-1) only for positive integer-multiple-of60 gaps; not proof trades should exist",
        "zero_volume_fraction":str(Decimal(counters["zero_volume_rows"])/Decimal(counters["rows_total"])),
        "UTC_label_dates":len(days),"date_rows_min":min(days.values()),"date_rows_max":max(days.values()),
        "dates_not_1440_rows":sum(v!=1440 for v in days.values()),
        "last_byte_newline":last_newline, "source_candle_open_or_close":"UNKNOWN",
        "publication_latency_and_revision_finality":"UNKNOWN", "no_repair_or_model_or_return_calculation":True}
    dump("full-scan-results.json",details)
    ST.update({"status":"COMPLETE","scan_complete":True,"rows_scanned":counters["rows_total"]})
    checkpoint()
except Exception as e:
    ST.update({"status":"STOPPED","error":type(e).__name__+":"+str(e),"end_utc":now()})
    checkpoint()
    print("STOPPED",ST["error"],flush=True)
    raise
finally:
    usage=resource.getrusage(resource.RUSAGE_SELF)
    dump("resource-receipt.json",{"start_utc":START["utc"],"end_utc":now(),"wall_seconds":time.monotonic()-T0,
         "user_CPU_seconds":usage.ru_utime,"system_CPU_seconds":usage.ru_stime,"peak_RSS_bytes":rss(),
         "single_process_single_thread_stdlib":True,"disk_bytes":sum(f.stat().st_size for f in P.iterdir() if f.is_file()),
         "limits":{"wall_seconds":900,"RSS_bytes":MAX_RSS,"disk_bytes":MAX_DISK},
         "new_model_runs":0,"returns_or_backtests":0,"new_payments":0,"network_GET_attempts":1})

