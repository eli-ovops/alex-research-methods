#!/usr/bin/env python3
"""One key entry, fixed read-only acquisition, then one offline unit. Default inert."""
import argparse
import datetime as dt
import getpass
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

OWNER = Path(__file__).resolve().parent
ROOT = OWNER.parent / "root"
INPUT = OWNER / "input"
BEGIN_CPU = time.process_time()
STATE = {"request_count": 0, "download_bytes": 0, "network_wait_seconds": 0.0,
         "download_measurement": "COMPLETE_APPLICATION_RESPONSE_BODY_BYTES"}
ACTIVE_START = None
RELEASE = None
CAPS = None
CPU_DEBIT = None
ACTIVE_DEBIT = None

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    with path.open("xb") as out:
        out.write(payload)
        out.flush()
        os.fsync(out.fileno())

def budget():
    if CPU_DEBIT + time.process_time() - BEGIN_CPU >= CAPS["cpu_seconds"]:
        raise RuntimeError("CPU_CAP")
    if ACTIVE_DEBIT + time.monotonic() - ACTIVE_START >= CAPS["active_seconds"]:
        raise RuntimeError("ACTIVE_CAP")
    if STATE["download_bytes"] > CAPS["download_bytes"]:
        raise RuntimeError("DOWNLOAD_CAP")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = rss if sys.platform == "darwin" else rss * 1024
    if rss > CAPS["rss_bytes"]:
        raise RuntimeError("RSS_CAP")
    if sum(p.stat().st_size for p in OWNER.rglob("*") if p.is_file()) > CAPS["disk_bytes"] - 4194304:
        raise RuntimeError("DISK_CAP")

def alarm(signum, frame):
    raise RuntimeError("BOUNDED_RESOURCE_TIMER")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("REDIRECT_REFUSED_NO_SECOND_REQUEST")

def get(url, key, destination=None, response_cap=4194304):
    budget()
    remaining_wait = CAPS["network_wait_seconds"] - STATE["network_wait_seconds"]
    if remaining_wait <= 0:
        raise RuntimeError("NETWORK_WAIT_CAP")
    started = time.monotonic()
    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, remaining_wait)
    response = None
    output = None
    chunks = []
    digest = hashlib.sha256()
    received = 0
    try:
        STATE["request_count"] += 1
        request = urllib.request.Request(url, method="GET", headers={
            "Authorization": "Bearer " + key, "Accept-Encoding": "identity"})
        response = urllib.request.build_opener(NoRedirect()).open(request, timeout=remaining_wait)
        if response.status != 200 or response.geturl() != url:
            raise RuntimeError("UNEXPECTED_HTTP_STATUS_OR_URL")
        length = response.headers.get("Content-Length")
        advertised = None if length is None else int(length)
        if advertised is not None and (advertised <= 0 or advertised > min(response_cap, CAPS["download_bytes"] - STATE["download_bytes"])):
            raise RuntimeError("DECLARED_RESPONSE_EXCEEDS_CAP")
        if destination is not None:
            output = destination.open("xb")
        while True:
            remaining = min(response_cap - received, CAPS["download_bytes"] - STATE["download_bytes"])
            if remaining <= 0:
                raise RuntimeError("RESPONSE_CAP_BEFORE_EOF")
            try:
                block = response.read(min(65536, remaining))
            except BaseException as error:
                partial = getattr(error, "partial", None)
                if isinstance(partial, bytes):
                    STATE["download_bytes"] += len(partial)
                    received += len(partial)
                STATE["download_measurement"] = "UNKNOWN_COMPLETE_TOTAL_OBSERVED_BYTES_ARE_LOWER_BOUND"
                raise
            if not block:
                break
            received += len(block)
            STATE["download_bytes"] += len(block)
            digest.update(block)
            if output is not None:
                output.write(block)
            else:
                chunks.append(block)
            budget()
        if advertised is not None and advertised != received:
            raise RuntimeError("CONTENT_LENGTH_MISMATCH")
        if output is not None:
            output.flush()
            os.fsync(output.fileno())
        identity = {"url": url, "http_status": 200, "observed_utc": now(), "bytes": received,
                    "sha256": digest.hexdigest(), "headers": {k: response.headers.get(k) for k in
                    ["Content-Length", "Content-Type", "Date", "Last-Modified", "ETag"]}}
        return (b"".join(chunks) if output is None else None), identity
    except BaseException:
        STATE["download_measurement"] = "UNKNOWN_COMPLETE_TOTAL_OBSERVED_BYTES_ARE_LOWER_BOUND"
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        STATE["network_wait_seconds"] += time.monotonic() - started
        if output is not None:
            output.close()
        if response is not None:
            response.close()

def timestamp(text):
    value = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.utcoffset() != dt.timedelta(0):
        raise RuntimeError("NON_UTC_PROVIDER_METADATA")
    return value

def check_scope(key):
    raw, info = get("https://api.tardis.dev/v1/api-key-info", key, response_cap=65536)
    entries = json.loads(raw)
    if not isinstance(entries, list):
        raise RuntimeError("KEY_SCOPE_FORMAT_UNKNOWN")
    found = {}
    for exchange, symbols in [("bitstamp", {"BTCUSD"}), ("kraken", {"BTC/USD", "BTC-USD"})]:
        for item in entries:
            if item.get("exchange") != exchange:
                continue
            if timestamp(item["from"]) <= timestamp("2026-09-02T00:00:00Z") and timestamp(item["to"]) >= timestamp("2026-09-04T00:00:00Z"):
                allowed = item.get("symbols")
                if not isinstance(allowed, list) or (allowed and not set(allowed).intersection(symbols)):
                    continue
                found[exchange] = {k: item.get(k) for k in ["exchange", "accessType", "from", "to", "symbols", "dataPlan"]}
                break
        if exchange not in found:
            raise RuntimeError("FIXED_DATES_NOT_IN_KEY_SCOPE")
    # Do not persist raw key-info response, headers or any credential.
    save(ROOT / "key-scope.json", {"url": info["url"], "http_status": 200,
         "observed_utc": info["observed_utc"], "required_scope": found})

def check_exports(key):
    targets = [("bitstamp", "BTCUSD", "book_snapshot_25"), ("kraken", "BTC-USD", "quotes")]
    out = []
    for exchange, symbol, kind in targets:
        raw, identity = get("https://api.tardis.dev/v1/exchanges/" + exchange, key)
        detail = json.loads(raw)
        data = detail["datasets"]
        matches = [x for x in data["symbols"] if x["id"] == symbol]
        if len(matches) != 1 or kind not in matches[0]["dataTypes"]:
            raise RuntimeError("EXACT_DATASET_NOT_IN_PROVIDER_METADATA")
        item = matches[0]
        if timestamp(data["exportedUntil"]) < timestamp("2026-09-04T00:00:00Z"):
            raise RuntimeError("FIXED_DAYS_NOT_EXPORTED")
        if timestamp(item["availableSince"]) > timestamp("2026-09-02T00:00:00Z"):
            raise RuntimeError("TARGET_NOT_AVAILABLE_AT_TRAIN_START")
        if item.get("availableTo") and timestamp(item["availableTo"]) < timestamp("2026-09-04T00:00:00Z"):
            raise RuntimeError("TARGET_NOT_AVAILABLE_THROUGH_TEST_DAY")
        out.append({"source": identity, "exchange": exchange, "target": item,
                    "exportedUntil": data["exportedUntil"]})
    save(ROOT / "target-export-metadata.json", {"targets": out})

def aggregate_usage():
    parent = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    parent_rss = parent.ru_maxrss if sys.platform == "darwin" else parent.ru_maxrss * 1024
    child_rss = child.ru_maxrss if sys.platform == "darwin" else child.ru_maxrss * 1024
    child_receipt = OWNER / "output/USAGE.json"
    if child_receipt.is_file():
        child_rss = max(child_rss, json.loads(child_receipt.read_text())["peak_rss_bytes"])
    return {"parent_cpu_seconds": time.process_time() - BEGIN_CPU,
            "child_cpu_seconds": child.ru_utime + child.ru_stime,
            "cpu_seconds_including_preparation": CPU_DEBIT + time.process_time() - BEGIN_CPU + child.ru_utime + child.ru_stime,
            "active_seconds_including_preparation": ACTIVE_DEBIT + time.monotonic() - ACTIVE_START,
            "combined_peak_rss_conservative_upper_bound": parent_rss + child_rss,
            "owner_disk_bytes": sum(p.stat().st_size for p in OWNER.rglob("*") if p.is_file()),
            "terminal_receipt_reserve_seconds": 5}

def main():
    global ACTIVE_START, RELEASE, CAPS, CPU_DEBIT, ACTIVE_DEBIT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        print("PREPARED_ONLY_NO_NETWORK_NO_KEY_INPUT_NO_MODEL")
        return 0
    RELEASE = json.loads((ROOT / "execution-release.json").read_text())
    if sha(Path(__file__)) != RELEASE["acquisition_code_sha256"] or sha(OWNER / "september_challenge.py") != RELEASE["model_code_sha256"] or sha(OWNER / "protocol.json") != RELEASE["protocol_sha256"]:
        raise RuntimeError("FROZEN_EXECUTION_IDENTITY_CHANGED")
    if (ROOT / "READY_FOR_KEY_INPUT.json").exists() or (ROOT / "ACQUISITION_STARTED.json").exists() or INPUT.exists() or (OWNER / "output").exists():
        raise RuntimeError("EXISTING_ATTEMPT_NO_RESTART")
    protocol = json.loads((OWNER / "protocol.json").read_text())
    CAPS = protocol["resource_caps"]
    CPU_DEBIT = RELEASE["preparation_cpu_debit_seconds"]
    ACTIVE_DEBIT = RELEASE["preparation_active_debit_seconds"]
    if CPU_DEBIT >= CAPS["cpu_seconds"] or ACTIVE_DEBIT >= CAPS["active_seconds"]:
        raise RuntimeError("PREPARATION_BUDGET_EXHAUSTED")
    save(ROOT / "READY_FOR_KEY_INPUT.json", {"utc": now(), "pid": os.getpid(),
         "status": "WAITING_FOR_USER_HIDDEN_INPUT", "requests_sent": 0,
         "key_stored": False, "single_input_entry": True})
    print("READY_FOR_ONE_HIDDEN_KEY_INPUT; four fixed files; no payment or trading", flush=True)
    key = getpass.getpass("Tardis Data API key (hidden, memory only): ").strip()
    if len(key) < 16 or len(key) > 4096 or any(c.isspace() for c in key) or key.startswith("http"):
        print("INVALID_KEY_INPUT_NO_REQUEST_SENT; STOP")
        return 2
    ACTIVE_START = time.monotonic()
    INPUT.mkdir()
    save(ROOT / "ACQUISITION_STARTED.json", {"utc": now(), "fixed_dates": ["2026-09-02", "2026-09-03"],
         "request_count_at_start": 0, "one_attempt": True, "no_payment": True})
    remaining_cpu = CAPS["cpu_seconds"] - CPU_DEBIT
    signal.signal(signal.SIGXCPU, alarm)
    current = time.process_time()
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(current + remaining_cpu), math.ceil(current + remaining_cpu) + 1))
    status = "STOPPED_NO_RETRY"
    try:
        check_scope(key)
        check_exports(key)
        files = []
        for spec in protocol["files"]:
            final = INPUT / spec["filename"]
            part = final.with_name(final.name + ".part")
            _, identity = get(spec["url"], key, destination=part, response_cap=CAPS["download_bytes"])
            if final.exists():
                raise RuntimeError("COMPLETE_INPUT_ALREADY_EXISTS")
            part.rename(final)
            files.append({"filename": spec["filename"], **identity})
            save(ROOT / ("acquired-" + spec["role"] + "-" + spec["label"] + ".json"), files[-1])
            print("ACQUIRED " + spec["role"] + " " + spec["label"], flush=True)
        key = None
        budget()
        usage = {"cpu_seconds": CPU_DEBIT + time.process_time() - BEGIN_CPU + 2,
                 "active_seconds": ACTIVE_DEBIT + time.monotonic() - ACTIVE_START + 2,
                 "download_bytes": STATE["download_bytes"], "network_wait_seconds": STATE["network_wait_seconds"],
                 "measured_acquisition_cpu_seconds": time.process_time() - BEGIN_CPU,
                 "conservative_preparation_cpu_debit_seconds": CPU_DEBIT,
                 "post_snapshot_parent_cpu_and_active_reserve_seconds": 2,
                 "preparation_active_debit_seconds": ACTIVE_DEBIT,
                 "preparation_debit_is_conservative_not_exact_project_measurement": True}
        save(OWNER / "input-receipts.json", {"files": files, "usage": usage})
        if sha(OWNER / "september_challenge.py") != RELEASE["model_code_sha256"]:
            raise RuntimeError("MODEL_CODE_CHANGED_AFTER_ACQUISITION")
        print("ACQUISITION_COMPLETE; starting the single offline unit", flush=True)
        remaining_active = CAPS["active_seconds"] - usage["active_seconds"]
        completed = subprocess.run([sys.executable, str(OWNER / "september_challenge.py"), "--mode", "run"],
            cwd=str(OWNER), capture_output=True, text=True, timeout=max(1, remaining_active))
        save(ROOT / "numeric-process.json", {"observed_utc": now(), "returncode": completed.returncode,
             "stdout": completed.stdout[:65536], "stderr": completed.stderr[:65536]})
        final_usage = aggregate_usage()
        resource_pass = (
            final_usage["cpu_seconds_including_preparation"] + 5 < CAPS["cpu_seconds"] and
            final_usage["active_seconds_including_preparation"] + 5 < CAPS["active_seconds"] and
            final_usage["combined_peak_rss_conservative_upper_bound"] <= CAPS["rss_bytes"] and
            final_usage["owner_disk_bytes"] <= CAPS["disk_bytes"] - 4194304 and
            STATE["download_bytes"] <= CAPS["download_bytes"] and
            STATE["network_wait_seconds"] <= CAPS["network_wait_seconds"] and
            STATE["download_measurement"] == "COMPLETE_APPLICATION_RESPONSE_BODY_BYTES")
        save(ROOT / "resource-acceptance.json", {"observed_utc": now(), "numeric_returncode": completed.returncode,
             "resources_pass": resource_pass, "counter_scope": "preparation debit plus measured parent and child",
             "this_is_not_forecast_profit_or_independence_acceptance": True, **final_usage, **STATE})
        status = "NUMERICAL_UNIT_RETURNED_WITHIN_BUDGET" if completed.returncode == 0 and resource_pass else "NUMERICAL_UNIT_STOPPED_OR_BUDGET_REJECTED"
        print(status, flush=True)
        return 0 if completed.returncode == 0 and resource_pass else 2
    except BaseException as error:
        key = None
        save(ROOT / "ACQUISITION_OR_UNIT_STOPPED.json", {"utc": now(), "exception_class": type(error).__name__,
             "http_status": error.code if isinstance(error, urllib.error.HTTPError) else None,
             "reason": error.args[0] if isinstance(error, RuntimeError) and error.args and
                 isinstance(error.args[0], str) and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789" for c in error.args[0]) else "DETAIL_REDACTED",
             "no_retry": True, "numeric_result_not_accepted": True})
        print("STOPPED_NO_RETRY; " + type(error).__name__, flush=True)
        return 2
    finally:
        key = None
        save(ROOT / "unit-usage.json", {"status": status, "observed_utc": now(), **STATE, **aggregate_usage(),
            "preparation_cpu_debit_seconds": CPU_DEBIT,
            "active_seconds_including_preparation": ACTIVE_DEBIT + time.monotonic() - ACTIVE_START,
            "spend_usd": 0, "secrets_persisted": False})

if __name__ == "__main__":
    raise SystemExit(main())
