#!/usr/bin/env python3
"""Fixed public gzip transport only; no numeric package, model or market parsing."""
import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import signal
import sys
import time
import urllib.error
import urllib.request

OWNER = Path(__file__).resolve().parent
BEGIN_CPU = time.process_time()
BEGIN_WALL = time.monotonic()
PLAN_SHA = "82661a061a639c5ad289fa8d8f64553befaeb4d54960934da705af7ebee5ffea"
URLS = {
    "B": "https://datasets.tardis.dev/v1/bitstamp/book_snapshot_25/2026/11/01/BTCUSD.csv.gz",
    "K": "https://datasets.tardis.dev/v1/kraken/quotes/2026/11/01/BTC-USD.csv.gz"}
NAMES = {"B": "bitstamp_book_snapshot_25_2026-11-01_BTCUSD.csv.gz",
         "K": "kraken_quotes_2026-11-01_BTC-USD.csv.gz"}
DATES = ("2026-11-02", "2026-11-03")
DOWNLOAD_CAP = 128 * 1024 ** 2
DISK_CAP = 192 * 1024 ** 2
RSS_CAP = 1024 ** 3
NETWORK_CAP = 1800
STATE = {"download_bytes": 0, "network_wait_seconds": 0., "request_count": 0}
PRIOR = None

def now():
    return dt.datetime.now(dt.timezone.utc)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    with (OWNER / name).open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=True, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())

def disk_bytes():
    return sum(p.stat().st_size for p in OWNER.rglob("*") if p.is_file())

def rss_bytes():
    n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if sys.platform == "darwin" else n * 1024)

def ledger():
    start = json.loads((OWNER / "execution-start.json").read_text())
    out = {"cpu_seconds": start["prior_known_cpu_debit_seconds"] + start["conservative_unmetered_preparation_cpu_debit_seconds"],
           "download_bytes": 0, "network_wait_seconds": 0.}
    for p in OWNER.glob("usage-*.json"):
        value = json.loads(p.read_text())
        for key in out:
            out[key] += value.get(key, 0)
    return out

def stop_alarm(signum, frame):
    raise TimeoutError("CUMULATIVE_NETWORK_WAIT_CAP")

def stop_cpu(signum, frame):
    raise RuntimeError("CUMULATIVE_CPU_CAP")

def budget():
    if PRIOR["cpu_seconds"] + time.process_time() - BEGIN_CPU >= 600:
        raise RuntimeError("CUMULATIVE_CPU_CAP")
    if PRIOR["download_bytes"] + STATE["download_bytes"] > DOWNLOAD_CAP:
        raise RuntimeError("CUMULATIVE_DOWNLOAD_CAP")
    if PRIOR["network_wait_seconds"] + STATE["network_wait_seconds"] >= NETWORK_CAP:
        raise RuntimeError("CUMULATIVE_NETWORK_WAIT_CAP")
    if disk_bytes() > DISK_CAP - 1048576 or rss_bytes() > RSS_CAP:
        raise RuntimeError("DISK_OR_RSS_CAP")

def allowed_date(clock):
    day = clock.date().isoformat()
    if day not in DATES or clock.hour < 12:
        raise RuntimeError("NOT_FIXED_NOV2_OR_NOV3_12UTC_CHECK")
    return day

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "REDIRECT_REFUSED_NO_SECOND_GET", headers, fp)

class Capture(io.RawIOBase):
    def __init__(self, upstream, sink):
        self.upstream, self.sink = upstream, sink
        self.sha, self.count, self.eof = hashlib.sha256(), 0, False
    def readable(self):
        return True
    def readinto(self, target):
        remaining_download = DOWNLOAD_CAP - PRIOR["download_bytes"] - STATE["download_bytes"]
        remaining_disk = DISK_CAP - disk_bytes() - 1048576
        if min(remaining_download, remaining_disk) <= 0:
            raise RuntimeError("DOWNLOAD_OR_DISK_CAP_NO_MORE_READ")
        raw = self.upstream.read(min(len(target), 65536, remaining_download, remaining_disk))
        if not raw:
            self.eof = True
            return 0
        STATE["download_bytes"] += len(raw)
        self.count += len(raw)
        self.sink.write(raw)
        self.sha.update(raw)
        budget()
        target[:len(raw)] = raw
        return len(raw)

def read_full_gzip(response, part):
    """One incoming compressed pass; decoded bytes discarded without CSV parsing."""
    with part.open("xb") as sink:
        capture = Capture(response, sink)
        with io.BufferedReader(capture, buffer_size=65536) as buffered:
            with gzip.GzipFile(fileobj=buffered, mode="rb") as zipped:
                while zipped.read(65536):
                    budget()
        sink.flush()
        os.fsync(sink.fileno())
    if not capture.eof:
        raise RuntimeError("COMPRESSED_EOF_NOT_REACHED")
    return {"bytes": capture.count, "sha256": capture.sha.hexdigest(), "gzip_crc_eof": True}

def download_one(label, day):
    budget()
    remaining = NETWORK_CAP - PRIOR["network_wait_seconds"] - STATE["network_wait_seconds"]
    began = time.monotonic()
    signal.signal(signal.SIGALRM, stop_alarm)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    response = None
    try:
        STATE["request_count"] += 1
        request = urllib.request.Request(URLS[label], method="GET", headers={"Accept-Encoding": "identity"})
        response = urllib.request.build_opener(NoRedirect()).open(request, timeout=remaining)
        if response.status != 200 or response.geturl() != URLS[label]:
            raise RuntimeError("UNEXPECTED_STATUS_OR_URL")
        header_length = response.headers.get("Content-Length")
        advertised = None if header_length is None else int(header_length)
        if advertised is not None and (advertised <= 0 or advertised > DOWNLOAD_CAP - PRIOR["download_bytes"] - STATE["download_bytes"] or advertised > DISK_CAP - disk_bytes() - 1048576):
            raise RuntimeError("ADVERTISED_BYTES_EXCEED_REMAINING_BUDGET")
        final = OWNER / "future-input" / NAMES[label]
        part = final.with_name(final.name + ".part")
        identity = read_full_gzip(response, part)
        if advertised is not None and identity["bytes"] != advertised:
            raise RuntimeError("CONTENT_LENGTH_MISMATCH")
        # Complete own newly-created input only; failed .part is never moved/deleted.
        if final.exists():
            raise RuntimeError("COMPLETE_PATH_ALREADY_EXISTS_NO_OVERWRITE")
        part.rename(final)
        completed = {"status": "COMPLETE", "url": URLS[label], "path": str(final),
                "http_status": 200, "observed_utc": now().isoformat(), **identity,
                "headers": {key: response.headers.get(key) for key in ("Content-Length", "Content-Type", "Date", "Last-Modified", "ETag")}}
        save("transport-complete-" + day + "-" + label + ".json", completed)
        return completed
    except urllib.error.HTTPError as error:
        # 404 only is the fixed not-yet-published branch; no same-day retry/body reread.
        result = {"status": "NOT_PUBLISHED_404" if error.code == 404 else "STOP_HTTP_ERROR", "http_status": error.code,
                  "url": URLS[label], "observed_utc": now().isoformat()}
        save("http-" + day + "-" + label + ".json", result)
        error.close()
        if error.code != 404:
            raise RuntimeError("HTTP_ERROR_STOP_NO_RETRY_" + str(error.code))
        return result
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        STATE["network_wait_seconds"] += time.monotonic() - began
        if response is not None:
            response.close()

def formal():
    day = allowed_date(now())
    if (OWNER / "TRANSPORT_HALTED.json").exists():
        raise RuntimeError("PREVIOUS_NON404_FAILURE_NO_RETRY")
    release_raw = (OWNER.parent / "root" / ("transport-" + day + "-release.json")).read_bytes()
    release = json.loads(release_raw)
    if release.get("transport_code_sha256") != digest(Path(__file__)) or release.get("proposal_sha256") != PLAN_SHA:
        raise RuntimeError("TRANSPORT_RELEASE_MISMATCH_NO_NETWORK")
    if release.get("model_seal_sha256") != digest(OWNER / "MODEL_SEALED.json"):
        raise RuntimeError("MODEL_SEAL_MISMATCH_NO_NETWORK")
    previous = {}
    if day == DATES[1]:
        previous = json.loads((OWNER / ("transport-result-" + DATES[0] + ".json")).read_text())["inputs"]
    save("TRANSPORT_STARTED_" + day + ".json", {"utc": now().isoformat(), "pid": os.getpid(), "single_date_check": True,
         "release_sha256": hashlib.sha256(release_raw).hexdigest(), "transport_code_sha256": digest(Path(__file__))})
    (OWNER / "future-input").mkdir(exist_ok=True)
    inputs = {}
    for label in ("B", "K"):
        old = previous.get(label)
        if old and old["status"] == "COMPLETE":
            path = OWNER / "future-input" / NAMES[label]
            if old["path"] != str(path) or not path.is_file() or path.stat().st_size != old["bytes"]:
                raise RuntimeError("PRIOR_COMPLETE_INPUT_CHANGED_NO_REDOWNLOAD")
            inputs[label] = {**old, "reused_complete_no_request": True}
        elif day == DATES[1] and (not old or old["status"] != "NOT_PUBLISHED_404"):
            raise RuntimeError("SECOND_DATE_ONLY_FOR_PREVIOUS_404")
        else:
            inputs[label] = download_one(label, day)
    result = {"status": "BOTH_COMPLETE_READY_FOR_ROOT_RELEASE" if all(x["status"] == "COMPLETE" for x in inputs.values()) else
              ("WAIT_ONLY_FIXED_NOV3_CHECK" if day == DATES[0] else "UNSCORED_MISSING_AFTER_FINAL_CHECK"),
              "day": day, "inputs": inputs, "request_count": STATE["request_count"], "network_wait_seconds": STATE["network_wait_seconds"],
              "no_model_or_CSV_price_parsing": True, "release_sha256": hashlib.sha256(release_raw).hexdigest()}
    save("transport-result-" + day + ".json", result)
    return result

def synthetic():
    assert allowed_date(dt.datetime(2026, 11, 2, 12, tzinfo=dt.timezone.utc)) == DATES[0]
    assert allowed_date(dt.datetime(2026, 11, 3, 12, tzinfo=dt.timezone.utc)) == DATES[1]
    for clock in (dt.datetime(2026, 11, 1, 12, tzinfo=dt.timezone.utc), dt.datetime(2026, 11, 2, 11, 59, tzinfo=dt.timezone.utc), dt.datetime(2026, 11, 4, 12, tzinfo=dt.timezone.utc)):
        rejected = False
        try:
            allowed_date(clock)
        except RuntimeError:
            rejected = True
        assert rejected
    refused = False
    try:
        NoRedirect().redirect_request(urllib.request.Request(URLS["B"]), io.BytesIO(), 302, "synthetic", {}, URLS["K"])
    except urllib.error.HTTPError:
        refused = True
    assert refused
    # In-memory gzip verifies the chosen reader's EOF/CRC semantics; no files/network.
    raw = gzip.compress(b"synthetic payload\n")
    assert gzip.decompress(raw) == b"synthetic payload\n"
    broken = raw[:-8] + bytes([raw[-8] ^ 1]) + raw[-7:]
    rejected = False
    try:
        gzip.decompress(broken)
    except (gzip.BadGzipFile, EOFError):
        rejected = True
    assert rejected
    result = {"status": "TRANSPORT_SYNTHETIC_PASS_NO_NETWORK", "network_requests": 0,
              "market_files_read": 0, "model_imports_or_fits": 0,
              "checks": ["two_fixed_dates_and_not_before_12UTC", "outside_dates_rejected", "redirect_refused_before_second_GET", "gzip_EOF_CRC_in_memory"],
              "fixed_URLs": URLS}
    save("transport-checks.json", result)
    return result

def main():
    global PRIOR
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic", "formal"))
    args = parser.parse_args()
    if args.mode is None:
        print("READY_ONLY_NO_NETWORK_NO_MARKET_READ")
        return 0
    PRIOR = ledger()
    signal.signal(signal.SIGXCPU, stop_cpu)
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(time.process_time() + 600 - PRIOR["cpu_seconds"]), math.ceil(time.process_time() + 600 - PRIOR["cpu_seconds"]) + 1))
    stage = "transport-synthetic" if args.mode == "synthetic" else "transport-" + now().date().isoformat()
    status = "STOP_TRANSPORT_ERROR_NO_RETRY"
    try:
        budget()
        result = synthetic() if args.mode == "synthetic" else formal()
        status = result["status"]
        print(json.dumps(result))
        return 0
    except BaseException as error:
        save("failure-" + stage + ".json", {"status": status, "type": type(error).__name__, "message": str(error)[:500], "utc": now().isoformat()})
        if args.mode == "formal":
            save("TRANSPORT_HALTED.json", {"stage": stage, "reason": type(error).__name__, "no_retry": True})
        print(json.dumps({"status": status, "error": type(error).__name__}))
        return 2
    finally:
        save("usage-" + stage + ".json", {"stage": stage, "status": status, "cpu_seconds": time.process_time() - BEGIN_CPU,
             "process_wall_seconds": time.monotonic() - BEGIN_WALL, "peak_rss_bytes": rss_bytes(), "owner_disk_bytes": disk_bytes(),
             **STATE, "completed_utc": now().isoformat(), "prior_cpu_debit_seconds": PRIOR["cpu_seconds"]})

if __name__ == "__main__":
    raise SystemExit(main())
