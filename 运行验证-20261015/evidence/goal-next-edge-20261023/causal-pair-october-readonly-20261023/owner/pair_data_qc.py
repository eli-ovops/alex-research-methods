#!/usr/bin/env python3
"""Fixed public-data QC only. Default invocation performs no market I/O."""
import argparse
from array import array
import csv
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
from decimal import Decimal, InvalidOperation

OWNER = Path(__file__).resolve().parent
BITSTAMP = Path("/Volumes/EXTERNAL/\u4e9a\u529b\u514b\u65af /\u8fd0\u884c\u9a8c\u8bc1-20261015/evidence/lobframe-data-entry-20261021/bitstamp_book_snapshot_25_2026-10-01_BTCUSD.csv.gz")
KRAKEN_URL = "https://datasets.tardis.dev/v1/kraken/quotes/2026/10/01/BTC-USD.csv.gz"
KRAKEN_BYTES = 12646757
BITSTAMP_BYTES = 26500836
BITSTAMP_SHA = "22d347447c1b12f422ea2ed16ba84725eb1b8c716a22aa6b53f775f7e2fd2fe0"
DAY_START = 1790812800000000
DAY_END = DAY_START + 86400 * 1000000
MEMORY_CAP = 256 * 1024 * 1024
DISK_CAP = 64 * 1024 * 1024
DOWNLOAD_CAP = 20 * 1024 * 1024
CPU_CAP = 120
WALL_CAP = 120
CORE = ("exchange", "symbol", "timestamp", "local_timestamp")
START_CPU = None

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def dump_new(name, value):
    p = OWNER / name
    with p.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=True, indent=2, allow_nan=False)
        f.write("\n")

def peak_rss_bytes():
    n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if sys.platform == "darwin" else n * 1024)

def check_budget():
    if START_CPU is not None and time.process_time() - START_CPU > CPU_CAP:
        raise RuntimeError("CPU_CAP")
    if peak_rss_bytes() > MEMORY_CAP:
        raise RuntimeError("RSS_CAP")

def alarm_stop(signum, frame):
    raise TimeoutError("ONE_DOWNLOAD_TOTAL_WALL_CAP")

def cpu_stop(signum, frame):
    raise RuntimeError("CPU_CAP")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code,
                                     "REDIRECT_REFUSED_NO_SECOND_GET", headers, fp)

def fixed_public_opener():
    return urllib.request.build_opener(NoRedirect())

class HashingReader(io.RawIOBase):
    """Single compressed input stream; optionally preserves exactly received bytes."""
    def __init__(self, upstream, expected_bytes, sink=None):
        super().__init__()
        self.upstream = upstream
        self.expected_bytes = expected_bytes
        self.sink = sink
        self.count = 0
        self.sha = hashlib.sha256()
        self.eof = False

    def readable(self):
        return True

    def readinto(self, target):
        check_budget()
        raw = self.upstream.read(min(len(target), 65536))
        if not raw:
            self.eof = True
            return 0
        self.count += len(raw)
        if self.sink is not None and self.count > DOWNLOAD_CAP:
            raise RuntimeError("DOWNLOAD_BYTE_CAP")
        if self.count > self.expected_bytes:
            raise RuntimeError("EXPECTED_SOURCE_BYTES_EXCEEDED")
        self.sha.update(raw)
        if self.sink is not None:
            self.sink.write(raw)
        target[:len(raw)] = raw
        return len(raw)

    def identity(self):
        return {"bytes": self.count, "sha256": self.sha.hexdigest(),
                "compressed_eof": self.eof}

def parse_stamp(value):
    if value is None or not value or not value.isascii() or not value.isdecimal():
        return None
    n = int(value)
    return n if 0 <= n < 10 ** 18 else None

def positive_number(value):
    if value is None or value == "":
        return None
    try:
        x = Decimal(value)
        return x if x.is_finite() and x > 0 else None
    except InvalidOperation:
        return None

class Source:
    """Every physical CSV row inspected once, including rows after the last grid."""
    def __init__(self, label, expected_exchange, expected_symbol, fields, rows):
        self.label = label
        self.expected_exchange = expected_exchange
        self.expected_symbol = expected_symbol
        self.fields = fields
        self.rows = rows
        self.previous_physical_row = None
        self.previous_local = None
        self.previous_exchange = None
        self.last = None
        self.pending = None
        self.exhausted = False
        self.s = {
            "label": label, "expected_exchange": expected_exchange,
            "expected_symbol": expected_symbol, "rows": 0,
            "header_missing": [], "duplicate_header_names": 0,
            "row_width_mismatch": 0, "adjacent_identical_full_rows": 0,
            "nonadjacent_global_duplicates": "UNKNOWN_NOT_CHECKED",
            "identity_mismatch": 0, "missing_or_invalid_local_timestamp": 0,
            "missing_or_invalid_exchange_timestamp": 0,
            "local_timestamp_backwards": 0, "local_timestamp_ties": 0,
            "exchange_timestamp_backwards": 0, "exchange_timestamp_ties": 0,
            "exchange_after_local": 0,
            "local_timestamp_outside_utc_day": 0,
            "exchange_timestamp_outside_utc_day": 0,
            "rows_with_bad_l1_numeric": 0, "crossed_bbo": 0,
            "locked_bbo": 0, "nonfinite_nonpositive_or_missing_by_field": {},
            "numeric_problem_categories_by_field": {},
            "first_local_us": None, "last_local_us": None,
            "first_exchange_us": None, "last_exchange_us": None,
            "whole_csv_eof": False, "gzip_crc_eof": False
        }
        need = list(CORE) + list(fields.values())
        names = getattr(rows, "fieldnames", None)
        if names is not None:
            self.s["header_missing"] = [n for n in need if n not in names]
            self.s["duplicate_header_names"] = len(names) - len(set(names))
            if self.s["header_missing"] or self.s["duplicate_header_names"]:
                raise RuntimeError(label + "_HEADER_NOT_ACCEPTED")

    def next_physical(self):
        try:
            row = next(self.rows)
        except StopIteration:
            self.exhausted = True
            self.s["whole_csv_eof"] = True
            return None
        self.s["rows"] += 1
        if self.s["rows"] % 4096 == 0:
            check_budget()
        # Include all parsed CSV fields, not just L1, for adjacent full-row equality.
        physical = tuple((k, tuple(v) if isinstance(v, list) else v)
                         for k, v in row.items())
        if physical == self.previous_physical_row:
            self.s["adjacent_identical_full_rows"] += 1
        self.previous_physical_row = physical
        if None in row or any(v is None for v in row.values()):
            self.s["row_width_mismatch"] += 1
        if row.get("exchange") != self.expected_exchange or row.get("symbol") != self.expected_symbol:
            self.s["identity_mismatch"] += 1
        local = parse_stamp(row.get("local_timestamp"))
        exch = parse_stamp(row.get("timestamp"))
        for name, value, previous in (
            ("local", local, self.previous_local),
            ("exchange", exch, self.previous_exchange)
        ):
            if value is None:
                self.s["missing_or_invalid_" + ("local_timestamp" if name == "local" else "exchange_timestamp")] += 1
                continue
            first_key = "first_" + name + "_us"
            if self.s[first_key] is None:
                self.s[first_key] = value
            self.s["last_" + name + "_us"] = value
            if not DAY_START <= value < DAY_END:
                self.s[name + "_timestamp_outside_utc_day"] += 1
            if previous is not None:
                if value < previous:
                    self.s[name + "_timestamp_backwards"] += 1
                elif value == previous:
                    self.s[name + "_timestamp_ties"] += 1
        if local is not None:
            self.previous_local = local
        if exch is not None:
            self.previous_exchange = exch
        if local is not None and exch is not None and exch > local:
            self.s["exchange_after_local"] += 1
        values = {}
        for semantic, column in self.fields.items():
            value = positive_number(row.get(column))
            values[semantic] = value
            if value is None:
                counts = self.s["nonfinite_nonpositive_or_missing_by_field"]
                counts[column] = counts.get(column, 0) + 1
                categories = self.s["numeric_problem_categories_by_field"].setdefault(column, {})
                original = row.get(column)
                if original is None or original == "":
                    category = "missing"
                else:
                    try:
                        number = Decimal(original)
                        category = "nonfinite" if not number.is_finite() else "nonpositive"
                    except InvalidOperation:
                        category = "invalid_numeric_text"
                categories[category] = categories.get(category, 0) + 1
        valid_l1 = all(v is not None for v in values.values())
        if not valid_l1:
            self.s["rows_with_bad_l1_numeric"] += 1
        elif values["bid"] > values["ask"]:
            self.s["crossed_bbo"] += 1
            valid_l1 = False
        elif values["bid"] == values["ask"]:
            self.s["locked_bbo"] += 1
        return (local, valid_l1, self.s["rows"])

    def at(self, tick):
        # No sorting, deduplication, nearest-future selection, or stale-row fallback.
        # Tied clocks: consumes through the final physical row with local <= tick.
        while not self.exhausted:
            if self.pending is None:
                self.pending = self.next_physical()
                if self.pending is None:
                    break
            local, valid, physical_row = self.pending
            if local is None:
                self.pending = None
                continue  # Admission fails; no usable timestamp to place this row.
            if local > tick:
                break
            self.last = self.pending
            self.pending = None
        return self.last

    def drain(self):
        # Pending has already been inspected; consume remaining rows solely for QC/CRC.
        self.pending = None
        while not self.exhausted:
            self.next_physical()

    def admission_issues(self):
        keys = ("identity_mismatch", "header_missing", "duplicate_header_names",
                "row_width_mismatch", "missing_or_invalid_local_timestamp",
                "local_timestamp_backwards", "local_timestamp_outside_utc_day")
        return [k for k in keys if self.s[k]] + (["EMPTY_SOURCE"] if self.s["rows"] == 0 else [])

def open_csv(raw):
    buffered = io.BufferedReader(raw, buffer_size=65536)
    zipped = gzip.GzipFile(fileobj=buffered, mode="rb")
    text = io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(text)
    return reader, text, zipped, buffered

def clock_grid(source, start=DAY_START, count=86400, step=1000000):
    clocks = array("q")
    flags = bytearray()
    source.s["fixed_grid_witnesses"] = []
    for i in range(count):
        tick = start + i * step
        row = source.at(tick)
        clocks.append(-1 if row is None else row[0])
        flags.append(0 if row is None else int(row[1]))
        if i in (0, 43200, 86399):
            pending = source.pending
            source.s["fixed_grid_witnesses"].append({
                "grid_index": i, "tick_us": tick,
                "selected_local_us": None if row is None else row[0],
                "selected_physical_data_row_1_based": None if row is None else row[2],
                "selected_l1_valid": None if row is None else row[1],
                "selected_record_age_us": None if row is None else tick - row[0],
                "next_local_us": None if pending is None else pending[0],
                "next_physical_data_row_1_based": None if pending is None else pending[2]
            })
    source.drain()
    return clocks, flags

def combine_clock_grids(left_grid, right_grid, start=DAY_START, count=86400, step=1000000):
    out = {
        "grid_start_us": start, "grid_points": count, "grid_step_us": step,
        "presence_definition": "latest physical row with valid local_timestamp <= grid tick; prices not emitted",
        "both_present": 0, "missing_both": 0, "missing_bitstamp": 0,
        "missing_kraken": 0, "both_present_and_l1_valid": 0,
        "both_age_le_1s": 0, "both_age_le_5s": 0,
        "max_age_gt_1s_le_5s": 0, "max_age_gt_5s": 0
    }
    left_clocks, left_flags = left_grid
    right_clocks, right_flags = right_grid
    for i in range(count):
        tick = start + i * step
        left, right = left_clocks[i], right_clocks[i]
        if left < 0 and right < 0:
            out["missing_both"] += 1
        elif left < 0:
            out["missing_bitstamp"] += 1
        elif right < 0:
            out["missing_kraken"] += 1
        else:
            out["both_present"] += 1
            if left_flags[i] and right_flags[i]:
                out["both_present_and_l1_valid"] += 1
            age = max(tick - left, tick - right)
            if age <= 1000000:
                out["both_age_le_1s"] += 1
            if age <= 5000000:
                out["both_age_le_5s"] += 1
            if 1000000 < age <= 5000000:
                out["max_age_gt_1s_le_5s"] += 1
            elif age > 5000000:
                out["max_age_gt_5s"] += 1
    assert sum(out[k] for k in ("both_present", "missing_both", "missing_bitstamp", "missing_kraken")) == count
    assert out["both_age_le_1s"] + out["max_age_gt_1s_le_5s"] + out["max_age_gt_5s"] == out["both_present"]
    return out

def pair_grid(a, b, start=DAY_START, count=86400, step=1000000):
    return combine_clock_grids(clock_grid(a, start, count, step),
                               clock_grid(b, start, count, step), start, count, step)

def fixed_fields(bitstamp=False):
    if bitstamp:
        return {"ask": "asks[0].price", "ask_qty": "asks[0].amount",
                "bid": "bids[0].price", "bid_qty": "bids[0].amount"}
    return {"ask": "ask_price", "ask_qty": "ask_amount",
            "bid": "bid_price", "bid_qty": "bid_amount"}

def synthetic_source(rows):
    return Source("synthetic", "x", "s", fixed_fields(), iter(rows))

def synthetic_row(clock, bid="10", ask="11"):
    return {"exchange": "x", "symbol": "s", "timestamp": str(clock),
            "local_timestamp": str(clock), "ask_price": ask, "ask_amount": "1",
            "bid_price": bid, "bid_amount": "1"}

def selftest():
    # Only tiny synthetic in-memory records, never source files or network.
    a = synthetic_source([synthetic_row(DAY_START + 1000000),
                          synthetic_row(DAY_START + 1000000, "NaN", "12"),
                          synthetic_row(DAY_START + 3000000)])
    assert a.at(DAY_START) is None
    assert a.at(DAY_START + 1000000) == (DAY_START + 1000000, False, 2)
    assert a.s["rows"] == 3  # future pending inspected, not selected
    assert a.s["local_timestamp_ties"] == 1
    b = synthetic_source([synthetic_row(DAY_START)])
    p = pair_grid(synthetic_source([synthetic_row(DAY_START)]), b, count=8)
    assert p["both_present"] == 8 and p["both_age_le_1s"] == 2
    assert p["both_age_le_5s"] == 6 and p["max_age_gt_5s"] == 2
    d = synthetic_source([synthetic_row(DAY_START + 2),
                          synthetic_row(DAY_START + 1)])
    d.drain()
    assert "local_timestamp_backwards" in d.admission_issues()
    r = synthetic_row(DAY_START)
    q = synthetic_source([r, dict(r)])
    q.drain()
    assert q.s["adjacent_identical_full_rows"] == 1
    bad = synthetic_source([synthetic_row(DAY_START, "NaN", "11"),
                            synthetic_row(DAY_START, "12", "11")])
    bad.drain()
    assert bad.s["rows_with_bad_l1_numeric"] == 1 and bad.s["crossed_bbo"] == 1
    raw_bytes = gzip.compress(b"synthetic header\n")
    h = HashingReader(io.BytesIO(raw_bytes), len(raw_bytes))
    rd, text, z, bf = open_csv(h)
    list(rd)
    assert h.eof and h.count == len(raw_bytes)
    assert h.sha.hexdigest() == hashlib.sha256(raw_bytes).hexdigest()
    # Corrupt gzip trailer must raise, and no repair/retry occurs.
    corrupt = raw_bytes[:-8] + b"\0" * 8
    try:
        list(open_csv(HashingReader(io.BytesIO(corrupt), len(corrupt)))[0])
        raise AssertionError("CRC corruption accepted")
    except (gzip.BadGzipFile, EOFError):
        pass
    result = {"status": "PASS_SYNTHETIC_SEMANTICS_ONLY", "created_utc": utc(),
              "market_files_read": 0, "network_requests": 0,
              "checks": ["asof_no_future", "physical_tie_retained", "age_buckets",
                         "backward_not_admitted", "adjacent_full_row_repeat",
                         "invalid_numeric_crossed", "single_stream_hash_crc",
                         "corrupt_crc_rejected"]}
    dump_new("synthetic-checks-v2.json", result)
    return result

def revision_checks():
    # Only changed semantics: no real transport or source file is opened.
    opener = fixed_public_opener()
    redirects = [h for h in opener.handlers if isinstance(h, urllib.request.HTTPRedirectHandler)]
    assert len(redirects) == 1 and isinstance(redirects[0], NoRedirect)
    rejected = False
    try:
        redirects[0].redirect_request(urllib.request.Request(KRAKEN_URL), None,
                                      302, "Found", {}, "https://example.invalid/redirect")
    except urllib.error.HTTPError as e:
        rejected = e.code == 302 and "NO_SECOND_GET" in str(e)
    assert rejected
    events = [synthetic_row(DAY_START + 2), synthetic_row(DAY_START + 3)]
    events[1]["timestamp"] = str(DAY_START + 1)
    source = synthetic_source(events)
    clock_grid(source, count=5)
    assert source.s["exchange_timestamp_backwards"] == 1
    assert source.admission_issues() == []
    backwards = synthetic_source([synthetic_row(DAY_START + 2), synthetic_row(DAY_START + 1)])
    backwards.drain()
    assert "local_timestamp_backwards" in backwards.admission_issues()
    missing = synthetic_row(DAY_START)
    missing["local_timestamp"] = ""
    source_missing = synthetic_source([missing])
    source_missing.drain()
    assert "missing_or_invalid_local_timestamp" in source_missing.admission_issues()
    rows = [synthetic_row(DAY_START),
            synthetic_row(DAY_START + 43200 * 1000000),
            synthetic_row(DAY_START + 43200 * 1000000, "NaN"),
            synthetic_row(DAY_START + 86399 * 1000000),
            synthetic_row(DAY_START + 86399 * 1000000 + 1)]
    witness_source = synthetic_source(rows)
    clock_grid(witness_source)
    witnesses = witness_source.s["fixed_grid_witnesses"]
    assert [w["grid_index"] for w in witnesses] == [0, 43200, 86399]
    assert [w["selected_physical_data_row_1_based"] for w in witnesses] == [1, 3, 4]
    assert witnesses[1]["selected_l1_valid"] is False
    for w in witnesses:
        assert w["selected_local_us"] <= w["tick_us"] < w["next_local_us"]
    result = {"status": "PASS_AFFECTED_SYNTHETIC_CHECKS_ONLY", "created_utc": utc(),
              "network_requests": 0, "market_files_read": 0,
              "checks": ["redirect_refused_before_follow", "exchange_backwards_report_only",
                         "local_backwards_missing_not_admitted", "three_fixed_witnesses",
                         "same_clock_last_physical", "selected_le_tick_lt_next"],
              "synthetic_witnesses": witnesses}
    dump_new("synthetic-revision-checks.json", result)
    return result

def formal():
    global START_CPU
    # Deliberately explicit mode: Root release must precede this invocation.
    START_CPU = time.process_time()
    dump_new("FORMAL_STARTED.json", {"started_utc": utc(), "single_run": True,
                                   "no_retry": True})
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_CAP, CPU_CAP + 1))
    signal.signal(signal.SIGXCPU, cpu_stop)
    csv.field_size_limit(1048576)
    result = {"started_utc": utc(), "status": "IN_PROGRESS",
              "request_count": 0, "bitstamp_pointer_expected_bytes": BITSTAMP_BYTES,
              "bitstamp_pointer_expected_sha256": BITSTAMP_SHA,
              "kraken_expected_bytes": KRAKEN_BYTES,
              "prices_or_grid_records_exported": False}
    handles = []
    a = b = ha = hb = None
    net_start = None
    try:
        if sys.platform != "darwin":
            raise RuntimeError("ENVIRONMENT_CHANGED_EXPECTED_MACOS")
        if str(BITSTAMP) != "/Volumes/EXTERNAL/\u4e9a\u529b\u514b\u65af /\u8fd0\u884c\u9a8c\u8bc1-20261015/evidence/lobframe-data-entry-20261021/bitstamp_book_snapshot_25_2026-10-01_BTCUSD.csv.gz":
            raise RuntimeError("FIXED_BITSTAMP_PATH_MISMATCH")
        if sum(p.stat().st_size for p in OWNER.iterdir() if p.is_file()) > DISK_CAP - DOWNLOAD_CAP:
            raise RuntimeError("OWNED_DISK_PRECHECK")
        net_start = time.monotonic()
        signal.signal(signal.SIGALRM, alarm_stop)
        signal.setitimer(signal.ITIMER_REAL, WALL_CAP)
        request = urllib.request.Request(KRAKEN_URL, method="GET",
                                         headers={"Accept-Encoding": "identity"})
        result["request_count"] = 1
        response = fixed_public_opener().open(request, timeout=WALL_CAP)
        handles.append(response)
        result["http_status"] = response.status
        result["response_url"] = response.geturl()
        result["headers"] = {k: response.headers.get(k) for k in
                             ("Content-Length", "Content-Type", "ETag", "Last-Modified", "Date")}
        if response.geturl() != KRAKEN_URL:
            raise RuntimeError("UNEXPECTED_REDIRECT")
        if response.status != 200:
            raise RuntimeError("HTTP_NOT_200")
        if response.headers.get("Content-Length") not in (None, str(KRAKEN_BYTES)):
            raise RuntimeError("ADVERTISED_BYTES_CHANGED")
        sink = (OWNER / "kraken_BTC-USD_quotes_2026-10-01.csv.gz.part").open("xb")
        handles.append(sink)
        hb = HashingReader(response, KRAKEN_BYTES, sink)
        br, bt, bz, bb = open_csv(hb)
        handles.extend([bb, bz, bt])
        b = Source("kraken", "kraken", "BTC-USD", fixed_fields(), br)
        kraken_grid = clock_grid(b)
        if not b.s["whole_csv_eof"] or not hb.eof:
            raise RuntimeError("KRAKEN_EOF_NOT_REACHED")
        b.s["gzip_crc_eof"] = True
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["download_and_kraken_qc_wall_seconds"] = time.monotonic() - net_start
        result["kraken_identity"] = hb.identity()
        if hb.count != KRAKEN_BYTES:
            raise RuntimeError("KRAKEN_BYTES_MISMATCH")
        sink.flush()
        os.fsync(sink.fileno())
        # Network processing is complete before opening the one fixed cache file.
        f = BITSTAMP.open("rb")
        handles.append(f)
        ha = HashingReader(f, BITSTAMP_BYTES)
        ar, at, az, ab = open_csv(ha)
        handles.extend([ab, az, at])
        a = Source("bitstamp", "bitstamp", "BTCUSD", fixed_fields(True), ar)
        bitstamp_grid = clock_grid(a)
        grid = combine_clock_grids(bitstamp_grid, kraken_grid)
        # CSV drain must have reached every gzip trailer and underlying stream EOF.
        for source, hashed in ((a, ha), (b, hb)):
            if not source.s["whole_csv_eof"] or not hashed.eof:
                raise RuntimeError("EOF_NOT_REACHED")
            source.s["gzip_crc_eof"] = True
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["download_through_pair_wall_seconds"] = time.monotonic() - net_start
        result["bitstamp_identity"] = ha.identity()
        result["kraken_identity"] = hb.identity()
        if ha.count != BITSTAMP_BYTES or ha.sha.hexdigest() != BITSTAMP_SHA:
            raise RuntimeError("BITSTAMP_IDENTITY_MISMATCH")
        if hb.count != KRAKEN_BYTES:
            raise RuntimeError("KRAKEN_BYTES_MISMATCH")
        sink.flush()
        os.fsync(sink.fileno())
        issues = {"bitstamp": a.admission_issues(), "kraken": b.admission_issues()}
        result["source_qc"] = {"bitstamp": a.s, "kraken": b.s}
        result["pair_grid"] = grid
        result["admission_issues"] = issues
        result["status"] = ("PASS_FIXED_DATA_QC_CONDITIONAL_PAIR_CLOCK"
                            if not any(issues.values()) else
                            "PAIR_CLOCK_NOT_ADMITTED_SOURCE_QC_ISSUES")
        result["pair_coverage_valid_for_admission"] = not any(issues.values())
        result["clock_scope"] = "supplier local_timestamp; no user latency or clock-error certification"
        result["market_feed_completeness_proven"] = False
        result["meaning"] = "data presence/age QC only; no price relation, signal, label, model, return, fills or strategy"
    except BaseException as e:
        signal.setitimer(signal.ITIMER_REAL, 0)
        result["status"] = "STOP_ERROR_NO_RETRY"
        result["error_type"] = type(e).__name__
        result["error_code_or_message"] = str(e)[:500]
        if isinstance(e, urllib.error.HTTPError):
            result["http_status"] = e.code
            result["error_response_headers"] = {k: e.headers.get(k) for k in
                                                ("Content-Length", "Content-Type", "Date")}
            # Read at most a bounded existing error response, not another request.
            try:
                signal.setitimer(signal.ITIMER_REAL, 2)
                error_body = e.read(65536)
                with (OWNER / "http-error-response.bin").open("xb") as error_file:
                    error_file.write(error_body)
                result["error_body_saved_bytes"] = len(error_body)
                result["error_body_sha256"] = hashlib.sha256(error_body).hexdigest()
                result["error_body_full_or_truncated"] = "UNKNOWN_BOUNDED_TO_65536"
            except BaseException as preserve_error:
                result["error_body_preservation"] = type(preserve_error).__name__
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        if ha is not None:
            result["bitstamp_partial_identity"] = ha.identity()
        if hb is not None:
            result["kraken_partial_identity"] = hb.identity()
        if a is not None:
            result["bitstamp_partial_qc"] = a.s
        if b is not None:
            result["kraken_partial_qc"] = b.s
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        for handle in reversed(handles):
            try:
                handle.close()
            except Exception:
                pass
        result["completed_utc"] = utc()
        result["cpu_seconds"] = time.process_time() - START_CPU
        result["peak_rss_bytes"] = peak_rss_bytes()
        result["owned_disk_bytes"] = sum(p.stat().st_size for p in OWNER.iterdir() if p.is_file())
        if result["owned_disk_bytes"] > DISK_CAP:
            result["status"] = "STOP_OWNED_DISK_CAP"
        result["source_passes"] = "each source at most one; partial failures not repeated"
        result["part_file_note"] = "full or partial Kraken compressed bytes preserved under .part; completion only result.json can certify"
        dump_new("result.json", result)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--revision-selftest", action="store_true")
    parser.add_argument("--formal-after-root-release", action="store_true")
    args = parser.parse_args()
    if sum((args.selftest, args.revision_selftest, args.formal_after_root_release)) > 1:
        raise SystemExit("choose one explicit mode")
    if args.selftest:
        print(json.dumps(selftest(), ensure_ascii=True))
    elif args.revision_selftest:
        print(json.dumps(revision_checks(), ensure_ascii=True))
    elif args.formal_after_root_release:
        output = formal()
        print(json.dumps({"status": output["status"], "request_count": output["request_count"]}))
        raise SystemExit(0 if output["status"].startswith("PASS_") else 2)
    else:
        print("READY_ONLY: no market files opened, no network. Root release required.")

