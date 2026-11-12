"""One documented public GET; local storage only, no market-content output."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
LOCAL = Path("/Users/USER/Library/Application Support/XTX-local-research/bitstamp-20220101-quotes-20261019")
URL = "https://datasets.tardis.dev/v1/bitstamp/quotes/2022/01/01/BTCUSD.csv.gz"
LIMIT = 64 * 1024 * 1024
PART = LOCAL / "BTCUSD-2022-01-01-quotes.csv.gz.partial"
FINAL = LOCAL / "BTCUSD-2022-01-01-quotes.csv.gz"
PRIVATE = LOCAL / "transport-private.json"
PUBLIC = ROOT / "transport-public.json"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def deadline(_signum, _frame):
    raise TimeoutError("fixed request deadline")


def main():
    os.umask(0o077)
    LOCAL.mkdir(mode=0o700, parents=True, exist_ok=False)
    private = {"url": URL, "start_UTC": utc(), "complete": False}
    public = {
        "url": URL,
        "start_UTC": private["start_UTC"],
        "complete": False,
        "request_method": "GET",
        "head_or_range_requests": 0,
        "credentials_or_accounts": False,
        "market_content_returned_to_AI": False,
        "market_statistics_returned_to_AI": False,
        "model_financial_or_trade_execution": False,
    }
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 60)
    try:
        request = urllib.request.Request(URL, method="GET")
        with urllib.request.urlopen(request, timeout=20) as response:
            public["http_status"] = response.status
            private["http_status"] = response.status
            if response.status != 200:
                raise RuntimeError("unsupported response status")
            length = response.headers.get("Content-Length")
            if length is not None and int(length) > LIMIT:
                raise RuntimeError("declared file exceeds fixed limit")
            private["declared_bytes"] = int(length) if length is not None else None
            private["content_type"] = response.headers.get("Content-Type")
            actual = 0
            digest = hashlib.sha256()
            first = None
            with PART.open("xb") as output:
                while True:
                    chunk = response.read(min(262144, LIMIT - actual + 1))
                    if not chunk:
                        break
                    if actual + len(chunk) > LIMIT:
                        raise RuntimeError("received file exceeds fixed limit")
                    if first is None:
                        first = chunk[:2]
                    output.write(chunk)
                    digest.update(chunk)
                    actual += len(chunk)
                output.flush()
                os.fsync(output.fileno())
            if first != b"\x1f\x8b":
                raise RuntimeError("not a gzip container")
            if length is not None and actual != int(length):
                raise RuntimeError("incomplete transfer")
            if FINAL.exists():
                raise RuntimeError("destination already exists")
            PART.rename(FINAL)
            private.update({"complete": True, "bytes": actual, "sha256": digest.hexdigest(), "path": str(FINAL)})
            public.update({"complete": True, "status": "HTTP_TRANSFER_COMPLETED_STORED_LOCALLY", "local_path": str(FINAL)})
    except urllib.error.HTTPError as error:
        private.update({"http_status": error.code, "error_class": type(error).__name__})
        public.update({"http_status": error.code, "status": "STOP_HTTP_ERROR_NO_RETRY"})
        error.close()
    except Exception as error:
        private["error_class"] = type(error).__name__
        public.update({"error_class": type(error).__name__, "status": "STOP_ACQUISITION_NOT_COMPLETED_NO_RETRY"})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        private["end_UTC"] = public["end_UTC"] = utc()
        with PRIVATE.open("x") as output:
            json.dump(private, output, ensure_ascii=False, indent=2)
            output.write("\n")
        with PUBLIC.open("x") as output:
            json.dump(public, output, ensure_ascii=False, indent=2)
            output.write("\n")
    print(json.dumps(public, ensure_ascii=False))
    return 0 if public["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
