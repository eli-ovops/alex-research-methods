"""One bounded, public, read-only acquisition. No retry or alternate route."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import http.client
import json
import re
import resource
import signal
import ssl
import sys
import time

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "request-manifest-v3.json"
OUT = ROOT / "public-read"
HOST = "eth-mainnet.g.alchemy.com"
PATH = "/v2/docs-demo"
TM = "0x7bcb64B2c9206a5B699eD43363f6F98D4776Cf5A"
SELECTORS = {"0x4aff96e1", "0x58569081"}


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def wall_timeout(signum, frame):
    raise TimeoutError("TOTAL_WALL_BUDGET")


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def quantity(value):
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value):
        raise ValueError("INVALID_HEX_QUANTITY")
    return int(value, 16)


def check_header(result):
    if not isinstance(result, dict):
        raise ValueError("NULL_OR_NONOBJECT_HEADER")
    quantity(result.get("number"))
    if not isinstance(result.get("hash"), str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", result["hash"]):
        raise ValueError("INVALID_BLOCK_HASH")
    return result["number"], result["hash"]


def run():
    raw_manifest = MANIFEST.read_bytes()
    spec = json.loads(raw_manifest)
    if spec["endpoint"] != "https://" + HOST + PATH or len(spec["steps"]) != 8:
        raise ValueError("MANIFEST_SCOPE_MISMATCH")
    review = json.loads((ROOT.parent / "review-owner/pre-execution-review.json").read_text())
    if review["must_fix"] or review["request_manifest_sha256"] != sha(raw_manifest):
        raise ValueError("UNREVIEWED_MANIFEST")
    if review["acquisition_script_sha256"] != sha(Path(__file__).read_bytes()):
        raise ValueError("UNREVIEWED_SCRIPT")
    if OUT.exists():
        raise ValueError("ONE_SHOT_OUTPUT_ALREADY_EXISTS_NO_RERUN")
    OUT.mkdir()
    signal.signal(signal.SIGALRM, wall_timeout)
    signal.setitimer(signal.ITIMER_REAL, 60.0)
    start = time.monotonic()
    started = utc()
    used_bytes = 0
    records = []
    bound = None
    scalar_values = {}
    last_send = None
    failure = None
    try:
        for i, step in enumerate(spec["steps"], 1):
            if step["slot"] != i:
                raise ValueError("STEP_ID_MISMATCH")
            method = step["method"]
            body = {"jsonrpc": "2.0", "id": i, "method": method}
            if i == 1:
                if method != "eth_chainId":
                    raise ValueError("METHOD_OUTSIDE_FIXED_SEQUENCE")
            elif method == "eth_getBlockByNumber" and i in (2, 3, 8):
                body["params"] = ["latest" if i == 2 else bound[0], False]
            elif method == "eth_call" and i in (4, 5, 6, 7):
                selector = step["input"]
                if selector not in SELECTORS or step["to"] != TM:
                    raise ValueError("CONTRACT_OR_SELECTOR_OUT_OF_SCOPE")
                body["params"] = [{"to": TM, "input": selector}, bound[0]]
            else:
                raise ValueError("METHOD_OUTSIDE_FIXED_SEQUENCE")
            if last_send is not None:
                time.sleep(max(0, 1.0 - (time.monotonic() - last_send)))
            remaining = 60.0 - (time.monotonic() - start)
            if remaining <= 0:
                raise TimeoutError("TOTAL_WALL_BUDGET")
            request_bytes = json.dumps(body, separators=(",", ":")).encode()
            (OUT / f"{i:02d}.request.json").write_bytes(request_bytes)
            record = {"slot": i, "method": method, "requested_at_utc": utc(),
                      "request_sha256": sha(request_bytes), "status": "STARTED"}
            records.append(record)
            dump(OUT / "in-progress.json", {"records": records, "started_at_utc": started})
            connection = http.client.HTTPSConnection(HOST, timeout=min(5.0, remaining), context=ssl.create_default_context())
            try:
                last_send = time.monotonic()
                connection.request("POST", PATH, body=request_bytes,
                                   headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "public-read-research/1.0"})
                response = connection.getresponse()
                record["HTTP_status"] = response.status
                record["content_type"] = response.getheader("Content-Type")
                record["content_encoding"] = response.getheader("Content-Encoding")
                raw = response.read(131072)
                record["received_at_utc"] = utc()
                record["request_round_trip_seconds"] = time.monotonic() - last_send
                record["body_bytes"] = len(raw)
                record["body_sha256"] = sha(raw)
                (OUT / f"{i:02d}.response.body").write_bytes(raw)
                used_bytes += len(raw)
                if len(raw) >= 131072 or used_bytes > 1048576:
                    raise ValueError("RESPONSE_BYTE_BUDGET")
                if response.status != 200:
                    raise ValueError("HTTP_NON200_STOP_NO_RETRY")
            finally:
                connection.close()
            obj = json.loads(raw)
            if not isinstance(obj, dict) or obj.get("jsonrpc") != "2.0" or obj.get("id") != i or "error" in obj or obj.get("result") is None:
                raise ValueError("JSONRPC_ERROR_NULL_OR_ENVELOPE_MISMATCH")
            result = obj["result"]
            if i == 1:
                if quantity(result) != 1:
                    raise ValueError("CHAIN_ID_MISMATCH")
            elif method == "eth_getBlockByNumber":
                header = check_header(result)
                if i == 2:
                    bound = header
                elif header != bound:
                    raise ValueError("BOUND_BLOCK_IDENTITY_MISMATCH")
            else:
                if not isinstance(result, str) or not re.fullmatch(r"0x[0-9a-fA-F]{64}", result):
                    raise ValueError("INVALID_UINT256_RETURN")
                value = int(result, 16)
                if selector in scalar_values and scalar_values[selector] != value:
                    raise ValueError("REPEATED_GETTER_MISMATCH")
                scalar_values[selector] = value
                record["decoded_uint256"] = value
            record["status"] = "VALIDATED"
            if time.monotonic() - start > 60:
                raise TimeoutError("TOTAL_WALL_BUDGET")
            dump(OUT / "in-progress.json", {"records": records, "bound_B_H": bound, "started_at_utc": started})
    except Exception as exc:
        failure = {"type": type(exc).__name__, "reason": str(exc)}
        if records and records[-1]["status"] == "STARTED":
            records[-1]["status"] = "STOPPED_ERROR"
    signal.setitimer(signal.ITIMER_REAL, 0)
    elapsed = time.monotonic() - start
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024
    if rss > 268435456 and failure is None:
        failure = {"type": "ResourceLimit", "reason": "RSS_LIMIT"}
    accepted = failure is None and len(records) == 8 and elapsed <= 60 and all(r["status"] == "VALIDATED" for r in records)
    receipt = {"status": "OBSERVED_FIXED_BLOCK_FUNCTIONAL_CONSISTENCY_PASS" if accepted else "STOPPED_NOT_PASSED",
               "started_at_utc": started, "finished_at_utc": utc(), "elapsed_seconds": elapsed,
               "request_manifest_sha256": sha(raw_manifest), "acquisition_script_sha256": sha(Path(__file__).read_bytes()),
               "records": records, "bound_B_H": bound, "decoded_getters": scalar_values,
               "requests_attempted": len(records), "response_body_bytes": used_bytes, "failure": failure,
               "peak_RSS_bytes": rss, "process_CPU_seconds": usage.ru_utime + usage.ru_stime,
               "request_round_trip_not_opportunity_discovery_latency": True,
               "not_finalized_canonical_atomic_independent_node_or_profit_proof": True,
               "retries_redirects_accounts_credentials_payments_WS_signatures_broadcast_models_backtests_trades": 0,
               "eth_call_semantics": "Read-only node message call; creates no blockchain transaction. Provider internal computation not independently instrumented."}
    dump(OUT / "receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "requests_attempted": len(records), "failure": failure, "elapsed_seconds": elapsed}))


if __name__ == "__main__":
    run()
