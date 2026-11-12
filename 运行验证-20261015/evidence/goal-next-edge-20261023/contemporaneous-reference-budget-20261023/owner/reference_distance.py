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
from decimal import Decimal, InvalidOperation

OWNER = Path(__file__).resolve().parent
BASE = OWNER.parent.parent
BITSTAMP = Path("/Volumes/EXTERNAL/\u4e9a\u529b\u514b\u65af /\u8fd0\u884c\u9a8c\u8bc1-20261015/evidence/lobframe-data-entry-20261021/bitstamp_book_snapshot_25_2026-10-01_BTCUSD.csv.gz")
KRAKEN = BASE / "source-pair-completion-20261023/owner/kraken_BTC-USD_quotes_2026-10-01.csv.gz.part"
SPECS = (("bitstamp", BITSTAMP, 26500836, "22d347447c1b12f422ea2ed16ba84725eb1b8c716a22aa6b53f775f7e2fd2fe0", "BTCUSD"),
         ("kraken", KRAKEN, 12646757, "0cf04f1e284f98705f399ce7a05800ce6ffaa7b218a52921ec3776b624fc7945", "BTC/USD"))
DAY_START = 1790812800000000
DAY_END = DAY_START + 86400 * 1000000
MEMORY_CAP = 256 * 1024 * 1024
DISK_CAP = 8 * 1024 * 1024
DOWNLOAD_CAP = 20 * 1024 * 1024  # inherited HashingReader sink guard; no sink/network used
CPU_CAP = 120
CORE = ("exchange", "symbol", "timestamp", "local_timestamp")
START_CPU = None
METRICS = ("S_B", "D", "absD", "U", "V")
LAYERS = ("all_valid", "both_age_le_1s", "max_age_gt_1s_le_5s", "max_age_gt_5s")
THRESHOLDS = (0, 1, 5, 10, 30, 40)

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
        self._observed_identities = {}
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
            "identity_mismatch": 0, "actual_identity_counts": [],
            "identity_groups_cap": 8, "identity_overflow_rows": 0,
            "identity_witness_string_limit": 128,
            "missing_or_invalid_local_timestamp": 0,
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
        actual_identity = (row.get("exchange"), row.get("symbol"))
        if actual_identity in self._observed_identities:
            self.s["actual_identity_counts"][self._observed_identities[actual_identity]]["rows"] += 1
        elif len(self._observed_identities) < 8:
            index = len(self._observed_identities)
            self._observed_identities[actual_identity] = index
            self.s["actual_identity_counts"].append({
                "exchange": None if actual_identity[0] is None else actual_identity[0][:128],
                "symbol": None if actual_identity[1] is None else actual_identity[1][:128],
                "witness_truncated": any(v is not None and len(v) > 128 for v in actual_identity),
                "rows": 1
            })
        else:
            self.s["identity_overflow_rows"] += 1
        if actual_identity != (self.expected_exchange, self.expected_symbol):
            self.s["identity_mismatch"] += 1
            raise RuntimeError(self.label + "_IDENTITY_MISMATCH")
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
        # New unit: fail closed on necessary fields/local clock; source-clock
        # backwards remains descriptive, preserving the reviewed clock definition.
        reject = ("row_width_mismatch", "missing_or_invalid_local_timestamp",
                  "missing_or_invalid_exchange_timestamp", "local_timestamp_backwards",
                  "local_timestamp_outside_utc_day", "exchange_timestamp_outside_utc_day",
                  "rows_with_bad_l1_numeric", "crossed_bbo")
        if any(self.s[k] for k in reject):
            raise RuntimeError(self.label + "_REQUIRED_FIELD_OR_LOCAL_CLOCK_ERROR")
        return (local, valid_l1, self.s["rows"], values["bid"], values["ask"])

    def at(self, tick):
        # No sorting, deduplication, nearest-future selection, or stale-row fallback.
        # Tied clocks: consumes through the final physical row with local <= tick.
        while not self.exhausted:
            if self.pending is None:
                self.pending = self.next_physical()
                if self.pending is None:
                    break
            local, valid, physical_row = self.pending[:3]
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


def cpu_stop(signum, frame):
    raise RuntimeError("CPU_CAP")

def fixed_fields(bitstamp=False):
    if bitstamp:
        return {"ask": "asks[0].price", "ask_qty": "asks[0].amount",
                "bid": "bids[0].price", "bid_qty": "bids[0].amount"}
    return {"ask": "ask_price", "ask_qty": "ask_amount",
            "bid": "bid_price", "bid_qty": "bid_amount"}

def age_layer(age_us):
    if age_us <= 1000000:
        return LAYERS[1]
    return LAYERS[2] if age_us <= 5000000 else LAYERS[3]

def describe_values(bid_b, ask_b, bid_k, ask_k):
    mid_b = (bid_b + ask_b) / 2
    mid_k = (bid_k + ask_k) / 2
    numerators = (10000 * (ask_b - bid_b), 10000 * (mid_k - mid_b),
                  10000 * (mid_k - bid_b), 10000 * (ask_b - mid_k))
    sb, d, u, v = (numerators[0] / mid_b, numerators[1] / mid_b,
                   numerators[2] / bid_b, numerators[3] / ask_b)
    # Exact Decimal cross-products for strict comparisons; no float threshold tests.
    crossings = [(numerators[2] > c * bid_b, numerators[3] > c * ask_b,
                  numerators[0] > 2 * c * mid_b)
                 for c in THRESHOLDS]
    return (sb, d, abs(d), u, v), crossings

def new_layers():
    return {key: {"n": 0, "values": {m: array("d") for m in METRICS},
                  "extreme_grid_indices": {m: {"min": None, "max": None} for m in METRICS},
                  "extreme_values": {},
                  "strict_threshold_counts": {str(c): {"U_gt_c": 0, "V_gt_c": 0, "both_gt_c": 0, "S_B_gt_2c": 0}
                                              for c in THRESHOLDS}}
            for key in LAYERS}

def add_point(layer, values, crossings, grid_index):
    layer["n"] += 1
    for metric, decimal_value in zip(METRICS, values):
        value = float(decimal_value)
        if not math.isfinite(value):
            raise RuntimeError("NONFINITE_METRIC_FLOAT")
        layer["values"][metric].append(value)
        ex = layer["extreme_values"].get(metric)
        if ex is None:
            layer["extreme_values"][metric] = [decimal_value, decimal_value]
            layer["extreme_grid_indices"][metric] = {"min": grid_index, "max": grid_index}
        else:
            if decimal_value < ex[0]:
                ex[0] = decimal_value
                layer["extreme_grid_indices"][metric]["min"] = grid_index
            if decimal_value > ex[1]:
                ex[1] = decimal_value
                layer["extreme_grid_indices"][metric]["max"] = grid_index
    for c, (u_gt, v_gt, width_gt) in zip(THRESHOLDS, crossings):
        counts = layer["strict_threshold_counts"][str(c)]
        counts["U_gt_c"] += int(u_gt)
        counts["V_gt_c"] += int(v_gt)
        counts["both_gt_c"] += int(u_gt and v_gt)
        counts["S_B_gt_2c"] += int(width_gt)
        assert not (u_gt and v_gt) or width_gt

def nearest_rank(sorted_values, numerator, denominator):
    n = len(sorted_values)
    if not n:
        return None
    return sorted_values[(numerator * n + denominator - 1) // denominator - 1]

def summarize_layer(layer):
    metrics = {}
    for metric in METRICS:
        ordered = sorted(layer["values"][metric])
        metrics[metric] = ({"min": ordered[0], "median": nearest_rank(ordered, 1, 2),
                           "p95": nearest_rank(ordered, 95, 100),
                           "p99": nearest_rank(ordered, 99, 100), "max": ordered[-1]}
                          if ordered else {key: "UNKNOWN" for key in ("min", "median", "p95", "p99", "max")})
    return {"denominator": layer["n"], "metrics_bp": metrics,
            "strict_threshold_counts": layer["strict_threshold_counts"],
            "extreme_grid_indices_first_tie": layer["extreme_grid_indices"]}

def witness(source, row, tick, i):
    pending = source.pending
    return {"grid_index": i, "tick_us": tick,
            "selected_local_us": None if row is None else row[0],
            "selected_physical_data_row_1_based": None if row is None else row[2],
            "selected_l1_valid": None if row is None else row[1],
            "selected_record_age_us": None if row is None else tick - row[0],
            "next_local_us": None if pending is None else pending[0],
            "next_physical_data_row_1_based": None if pending is None else pending[2]}

def formal():
    global START_CPU
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol_sha = hashlib.sha256((OWNER.parent / "protocol.md").read_bytes()).hexdigest()
    release_raw = (OWNER.parent / "root-release.json").read_bytes()
    release = json.loads(release_raw)
    if release.get("code_sha256") != code_sha or release.get("protocol_sha256") != protocol_sha:
        raise SystemExit("ROOT_RELEASE_MISMATCH_NO_SOURCE_READ")
    START_CPU = time.process_time()
    dump_new("FORMAL_STARTED.json", {"utc": utc(), "single_run": True,
             "code_sha256": code_sha, "protocol_sha256": protocol_sha,
             "root_release_sha256": hashlib.sha256(release_raw).hexdigest(), "pid": os.getpid()})
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_CAP, CPU_CAP + 1))
    signal.signal(signal.SIGXCPU, cpu_stop)
    csv.field_size_limit(1048576)
    wall = time.monotonic()
    result = {"started_utc": utc(), "status": "IN_PROGRESS", "network_requests": 0,
              "code_sha256": code_sha, "protocol_sha256": protocol_sha,
              "root_release_sha256": hashlib.sha256(release_raw).hexdigest(),
              "source_passes": "one sequential pass per fixed local source; no retry"}
    handles, sources, hashes = [], {}, {}
    try:
        if sys.platform != "darwin":
            raise RuntimeError("ENVIRONMENT_CHANGED_EXPECTED_MACOS")
        if sum(p.stat().st_size for p in OWNER.iterdir() if p.is_file()) > DISK_CAP - 1048576:
            raise RuntimeError("OWNED_DISK_PRECHECK")
        for label, path, size, sha, symbol in SPECS:
            f = path.open("rb")
            handles.append(f)
            hashed = HashingReader(f, size)
            hashes[label] = hashed
            rows, text, zipped, buffered = open_csv(hashed)
            handles.extend((buffered, zipped, text))
            sources[label] = Source(label, label, symbol, fixed_fields(label == "bitstamp"), rows)
            sources[label].s["fixed_grid_witnesses"] = []
        layers = new_layers()
        counts = {"grid_points": 86400, "both_present": 0, "missing_both": 0,
                  "missing_bitstamp": 0, "missing_kraken": 0, "invalid_l1": 0,
                  "unknown": 0}
        for i in range(86400):
            if i % 1024 == 0:
                check_budget()
            tick = DAY_START + i * 1000000
            b = sources["bitstamp"].at(tick)
            k = sources["kraken"].at(tick)
            if i in (0, 43200, 86399):
                for label, row in (("bitstamp", b), ("kraken", k)):
                    sources[label].s["fixed_grid_witnesses"].append(witness(sources[label], row, tick, i))
            if b is None or k is None:
                key = "missing_both" if b is None and k is None else ("missing_bitstamp" if b is None else "missing_kraken")
                counts[key] += 1
                counts["unknown"] += 1
                continue
            counts["both_present"] += 1
            if not b[1] or not k[1]:
                counts["invalid_l1"] += 1
                counts["unknown"] += 1
                continue
            age = max(tick - b[0], tick - k[0])
            if age < 0:
                raise RuntimeError("ASOF_NEGATIVE_AGE")
            values, crossings = describe_values(b[3], b[4], k[3], k[4])
            add_point(layers["all_valid"], values, crossings, i)
            add_point(layers[age_layer(age)], values, crossings, i)
        for label, path, size, sha, symbol in SPECS:
            source, hashed = sources[label], hashes[label]
            source.drain()
            if not source.s["whole_csv_eof"] or not hashed.eof:
                raise RuntimeError(label + "_EOF_NOT_REACHED")
            source.s["gzip_crc_eof"] = True
            if hashed.count != size or hashed.sha.hexdigest() != sha:
                raise RuntimeError(label + "_SOURCE_FINGERPRINT_MISMATCH")
            if source.admission_issues():
                raise RuntimeError(label + "_SOURCE_NOT_ADMITTED")
        expected = {"all_valid": 86398, "both_age_le_1s": 76512,
                    "max_age_gt_1s_le_5s": 9608, "max_age_gt_5s": 278}
        actual = {key: layers[key]["n"] for key in LAYERS}
        if actual != expected or counts != {"grid_points": 86400, "both_present": 86398,
                                            "missing_both": 2, "missing_bitstamp": 0,
                                            "missing_kraken": 0, "invalid_l1": 0, "unknown": 2}:
            raise RuntimeError("PRIOR_COVERAGE_MISMATCH_STOP_INTERPRETATION")
        assert sum(actual[key] for key in LAYERS[1:]) == actual["all_valid"]
        result["grid_counts"] = counts
        result["layers"] = {key: summarize_layer(layers[key]) for key in LAYERS}
        check_budget()
        result["age_le_5s_cumulative_denominator"] = actual[LAYERS[1]] + actual[LAYERS[2]]
        result["quantiles"] = "nearest rank ceil(p*n)-1; metrics stored as finite binary64 after Decimal formulas"
        result["thresholds"] = "strict U>c,V>c,both,S_B>2c; Decimal cross-products before division; c=0/1/5/10/30/40bp"
        result["layer_relation"] = "all_valid is cumulative union of three mutually exclusive age layers; each second is not an independent obtainable trade"
        result["meaning"] = "contemporaneous quote-to-reference distance only; K is input, not certified fair price, future target, return, or profitability bound"
        result["status"] = "PASS_CONTEMPORANEOUS_DISTANCE_DESCRIPTIVE_ONLY"
    except BaseException as error:
        result["status"] = "STOP_ERROR_NO_RETRY_NO_INTERPRETATION"
        result["error_type"] = type(error).__name__
        result["error_code_or_message"] = str(error)[:500]
    finally:
        result["source_qc"] = {label: source.s for label, source in sources.items()}
        result["source_identities"] = {label: hashed.identity() for label, hashed in hashes.items()}
        for handle in reversed(handles):
            try:
                handle.close()
            except Exception:
                pass
        result["completed_utc"] = utc()
        result["wall_seconds"] = time.monotonic() - wall
        result["cpu_seconds"] = time.process_time() - START_CPU
        result["peak_rss_bytes"] = peak_rss_bytes()
        result["owned_disk_bytes_before_result"] = sum(p.stat().st_size for p in OWNER.iterdir() if p.is_file())
        if result["owned_disk_bytes_before_result"] > DISK_CAP:
            result["status"] = "STOP_DISK_CAP_NO_INTERPRETATION"
        dump_new("result.json", result)
    return result

def preparation_checks():
    # Only new formulas/strict boundaries/ranks and changed tuple/asof wiring.
    dec = Decimal
    values, crossings = describe_values(dec("100"), dec("102"), dec("99"), dec("103"))
    assert values == (dec(20000) / 101, dec(0), dec(0), dec(100), dec(10000) / 102)
    assert crossings[-1] == (True, True, True)
    low_values, low_flags = describe_values(dec("100"), dec("102"), dec("98"), dec("100"))
    assert low_values[1] < 0 and low_flags[0][:2] == (False, True)
    # U exactly 0/1/5/10/30/40 must never pass its own strict threshold.
    for j, c in enumerate(THRESHOLDS):
        mid_k = dec(100) * (1 + dec(c) / 10000)
        _, flags = describe_values(dec(100), dec(110), mid_k, mid_k)
        assert flags[j][0] is False
    # V exact boundary uses ask=100, Kmid=100*(1-c/10000).
    for j, c in enumerate(THRESHOLDS):
        mid_k = dec(100) * (1 - dec(c) / 10000)
        _, flags = describe_values(dec(90), dec(100), mid_k, mid_k)
        assert flags[j][1] is False
    # S_B=2c equality is excluded, with a midpoint fixed at exactly 100.
    for j, c in enumerate(THRESHOLDS):
        width = dec(c) / 100
        _, flags = describe_values(dec(100) - width, dec(100) + width, dec(100), dec(100))
        assert flags[j][2] is False
    assert nearest_rank([1, 2, 3, 4], 1, 2) == 2
    assert nearest_rank([1, 2, 3, 4], 95, 100) == 4
    empty = summarize_layer(new_layers()["all_valid"])
    assert empty["metrics_bp"]["U"]["median"] == "UNKNOWN"
    assert [age_layer(x) for x in (1000000, 1000001, 5000000, 5000001)] == [LAYERS[1], LAYERS[2], LAYERS[2], LAYERS[3]]
    def row(clock, bid, ask):
        return {"exchange": "x", "symbol": "s", "timestamp": str(clock),
                "local_timestamp": str(clock), "bid_price": bid, "ask_price": ask,
                "bid_amount": "1", "ask_amount": "1"}
    s = Source("synthetic", "x", "s", fixed_fields(), iter([
        row(DAY_START + 1, "100", "102"), row(DAY_START + 1, "101", "103"),
        row(DAY_START + 2, "102", "104")]))
    assert s.at(DAY_START) is None
    chosen = s.at(DAY_START + 1)
    assert chosen[2:] == (2, dec("101"), dec("103"))
    assert s.pending[0] == DAY_START + 2
    receipt = {"status": "PASS_CHANGED_BOUNDARIES_ONLY", "created_utc": utc(),
               "network_requests": 0, "market_source_reads": 0,
               "checks": ["five_formula_denominators", "strict_U_V_threshold_equalities",
                          "nearest_rank_even_median", "empty_UNKNOWN",
                          "age_1s_5s_boundaries", "extended_tuple_last_tie_no_future"],
               "synthetic_not_market_evidence": True}
    receipt["checks"].extend(["negative_D_and_mixed_signs", "width_S_B_strict_2c_equalities", "both_gt_implies_width_gt"])
    dump_new("preparation-checks-final.json", receipt)
    return receipt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preparation-selftest", action="store_true")
    parser.add_argument("--formal-after-root-release", action="store_true")
    args = parser.parse_args()
    if args.preparation_selftest and args.formal_after_root_release:
        raise SystemExit("CHOOSE_ONE_MODE")
    if args.preparation_selftest:
        print(json.dumps(preparation_checks()))
    elif args.formal_after_root_release:
        output = formal()
        print(json.dumps({"status": output["status"], "network_requests": 0}))
        raise SystemExit(0 if output["status"].startswith("PASS_") else 2)
    else:
        print("READY_ONLY_NO_SOURCE_READ_ROOT_RELEASE_REQUIRED")

