#!/usr/bin/env python3
"""Prepared offline historical challenge; no execution or market IO by default.

The numeric definitions below are copied verbatim from the original sealed
challenge. This module has not been imported or run during preparation.
The optional formal run needs four locally acquired files and real acquisition
receipts. It cannot register an account, acquire data or read credentials.
"""
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
import threading
import time

OWNER = Path(__file__).resolve().parent
INPUT = OWNER / "input"
OUTPUT = OWNER / "output"
PROTOCOL_SHA256 = "4313311d8ebdfdcf2e5cf9f6c931746e9a5bc5a3da231a4256fb49ca83764b1c"
TRAIN_DAY = "2026-09-02"
CHALLENGE_DAY = "2026-09-03"
M0_NAMES = ["B_log_mid_change_100ms_bp", "B_log_mid_change_500ms_bp", "B_relative_spread_bp", "B_L1_imbalance"]
M1_NAMES = M0_NAMES + ["K_log_mid_change_100ms_bp", "K_log_mid_change_500ms_bp", "log_mid_basis_minus_30_prior_anchor_mean_bp"]
np = None
RUN_CPU_START = None
RUN_WALL_START = None
PRIOR_CPU = None
PRIOR_ACTIVE = None
CAPS = None
WATCHDOG_STOP = threading.Event()
WATCHDOG_THREAD = None

def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def small_sha(path):
    return sha_bytes(path.read_bytes())

def get_numpy():
    global np
    if np is None:
        import numpy
        np = numpy
        if np.__version__ != "2.0.2":
            raise RuntimeError("FROZEN_NUMPY_VERSION_MISMATCH")
    return np

def environment():
    get_numpy()
    from contextlib import redirect_stdout
    capture = io.StringIO()
    with redirect_stdout(capture):
        np.show_config()
    return {"python": sys.version, "executable": sys.executable, "numpy": np.__version__,
            "numpy_config": capture.getvalue(), "platform": sys.platform,
            "requested_numeric_threads": 1,
            "thread_environment": {k: os.environ[k] for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
            "actual_blas_thread_count": "UNKNOWN", "actual_model_effort": "UNKNOWN"}

def day_start(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp()) * 1000000

def grid(day):
    get_numpy()
    out = day_start(day) + np.arange(60, 86400, 2, dtype=np.int64) * 1000000
    assert len(out) == 43170 and out[-1] == day_start(day) + 86398 * 1000000
    return out

class HashedStream(io.RawIOBase):
    def __init__(self, upstream, expected_bytes):
        self.upstream, self.expected_bytes = upstream, expected_bytes
        self.count, self.eof = 0, False
        self.sha = hashlib.sha256()
    def readable(self):
        return True
    def readinto(self, target):
        raw = self.upstream.read(min(len(target), 65536))
        if not raw:
            self.eof = True
            return 0
        self.count += len(raw)
        if self.count > self.expected_bytes:
            raise RuntimeError("SOURCE_BYTES_EXCEEDED")
        self.sha.update(raw)
        target[:len(raw)] = raw
        return len(raw)

def read_source(label, path, expected_bytes, expected_sha, day):
    """Only invoked in released formal modes; one compressed sequential pass."""
    fields = ({"bid": "bids[0].price", "ask": "asks[0].price", "bq": "bids[0].amount", "aq": "asks[0].amount"}
              if label == "B" else {"bid": "bid_price", "ask": "ask_price", "bq": "bid_amount", "aq": "ask_amount"})
    exchange, symbol = ("bitstamp", "BTCUSD") if label == "B" else ("kraken", "BTC/USD")
    data = {k: array("q" if k == "local" else "d") for k in ("local", "bid", "ask", "bq", "aq")}
    start, previous, rows, ties = day_start(day), None, 0, 0
    with path.open("rb") as upstream:
        hashed = HashedStream(upstream, expected_bytes)
        with io.BufferedReader(hashed, buffer_size=65536) as buffered:
            with gzip.GzipFile(fileobj=buffered, mode="rb") as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="") as text:
                    reader = csv.DictReader(text)
                    required = ["exchange", "symbol", "timestamp", "local_timestamp"] + list(fields.values())
                    names = reader.fieldnames or []
                    if len(names) != len(set(names)) or any(k not in names for k in required):
                        raise RuntimeError(label + "_HEADER_ERROR")
                    for row in reader:
                        rows += 1
                        if rows % 4096 == 0:
                            check_budget()
                        if None in row or any(v is None for v in row.values()):
                            raise RuntimeError(label + "_ROW_WIDTH_ERROR")
                        if row["exchange"] != exchange or row["symbol"] != symbol:
                            raise RuntimeError(label + "_IDENTITY_ERROR")
                        local_text = row["local_timestamp"]
                        if not local_text.isascii() or not local_text.isdecimal():
                            raise RuntimeError(label + "_LOCAL_TIMESTAMP_ERROR")
                        local = int(local_text)
                        if not start <= local < start + 86400000000 or (previous is not None and local < previous):
                            raise RuntimeError(label + "_LOCAL_ORDER_OR_DAY_ERROR")
                        ties += int(previous == local)
                        previous = local
                        values = {k: float(row[column]) for k, column in fields.items()}
                        if not all(math.isfinite(v) and v > 0 for v in values.values()) or values["bid"] > values["ask"]:
                            raise RuntimeError(label + "_L1_INVALID")
                        data["local"].append(local)
                        for k, value in values.items():
                            data[k].append(value)
                    if not hashed.eof:
                        raise RuntimeError(label + "_COMPRESSED_EOF_MISSING")
    identity = {"path": str(path), "bytes": hashed.count, "sha256": hashed.sha.hexdigest(),
                "rows": rows, "same_local_timestamp": ties, "gzip_crc_eof": True,
                "exchange": exchange, "symbol": symbol}
    if rows == 0 or hashed.count != expected_bytes or hashed.sha.hexdigest() != expected_sha:
        raise RuntimeError(label + "_SOURCE_FINGERPRINT_ERROR")
    get_numpy()
    return {k: np.frombuffer(v, dtype=np.int64 if k == "local" else np.float64) for k, v in data.items()}, identity

def sample(source, anchors, strict, age_cap_us):
    indices = np.searchsorted(source["local"], anchors, side="left" if strict else "right") - 1
    present = indices >= 0
    local = np.full(len(anchors), -1, dtype=np.int64)
    local[present] = source["local"][indices[present]]
    age = np.full(len(anchors), np.iinfo(np.int64).max, dtype=np.int64)
    age[present] = anchors[present] - local[present]
    valid = present & (age >= 0) & (age <= age_cap_us)
    values = {k: np.full(len(anchors), np.nan) for k in ("bid", "ask", "bq", "aq")}
    for k in values:
        values[k][present] = source[k][indices[present]]
    return {**values, "mid": (values["bid"] + values["ask"]) / 2,
            "valid": valid, "local": local, "physical_row": indices + 1, "age_us": age}

def make_features(b, k, ticks):
    """All eligibility depends only on strict pre-anchor records; no labels here."""
    requirements, reason_counts = [], {}
    first_reason = np.zeros(len(ticks), dtype=np.uint16)
    def take(source, anchors, cap, name):
        item = sample(source, anchors, True, cap)
        reason_counts[name] = {"total_invalid": int(np.count_nonzero(~item["valid"])),
                              "missing_before_anchor": int(np.count_nonzero(item["local"] < 0)),
                              "present_but_age_exceeded": int(np.count_nonzero((item["local"] >= 0) & ~item["valid"]))}
        first_reason[(first_reason == 0) & ~item["valid"]] = len(requirements) + 1
        requirements.append(item["valid"])
        return item
    bn = take(b, ticks, 1000000, "B_current_missing_or_age_gt_1s")
    kn = take(k, ticks, 1000000, "K_current_missing_or_age_gt_1s")
    b100 = take(b, ticks - 100000, 5000000, "B_100ms_anchor_missing_or_age_gt_5s")
    b500 = take(b, ticks - 500000, 5000000, "B_500ms_anchor_missing_or_age_gt_5s")
    k100 = take(k, ticks - 100000, 5000000, "K_100ms_anchor_missing_or_age_gt_5s")
    k500 = take(k, ticks - 500000, 5000000, "K_500ms_anchor_missing_or_age_gt_5s")
    basis_sum = np.zeros(len(ticks))
    for seconds in range(2, 61, 2):
        ba = take(b, ticks - seconds * 1000000, 5000000, "B_basis_anchor_minus_" + str(seconds) + "s_invalid")
        ka = take(k, ticks - seconds * 1000000, 5000000, "K_basis_anchor_minus_" + str(seconds) + "s_invalid")
        basis_sum += 10000 * np.log(ka["mid"] / ba["mid"])
    x0 = np.column_stack((10000 * np.log(bn["mid"] / b100["mid"]),
                          10000 * np.log(bn["mid"] / b500["mid"]),
                          10000 * (bn["ask"] - bn["bid"]) / bn["mid"],
                          (bn["bq"] - bn["aq"]) / (bn["bq"] + bn["aq"])))
    x1 = np.column_stack((x0, 10000 * np.log(kn["mid"] / k100["mid"]),
                          10000 * np.log(kn["mid"] / k500["mid"]),
                          10000 * np.log(kn["mid"] / bn["mid"]) - basis_sum / 30))
    valid = np.logical_and.reduce(requirements)
    if not np.all(np.isfinite(x0[valid])) or not np.all(np.isfinite(x1[valid])):
        raise RuntimeError("NONFINITE_ELIGIBLE_FEATURE")
    x0[~valid] = np.nan
    x1[~valid] = np.nan
    naive = np.full(len(ticks), np.nan)
    naive[valid] = 10000 * (bn["bid"][valid] / bn["ask"][valid] - 1)
    counts = {"fixed_grid": len(ticks), "common_valid_predictions": int(valid.sum()),
              "missing_or_stale_common": int((~valid).sum()), "overlapping_reasons": reason_counts,
              "first_reason_order": list(reason_counts),
              "first_reason_exclusive_counts": {str(i): int((first_reason == i).sum()) for i in range(len(requirements) + 1)}}
    witnesses = []
    for i in (0, len(ticks) // 2, len(ticks) - 1):
        witnesses.append({"grid_index": i, "tick_us": int(ticks[i]), "common_valid": bool(valid[i]),
                          "B_selected_local_us": int(bn["local"][i]), "K_selected_local_us": int(kn["local"][i]),
                          "B_physical_row": int(bn["physical_row"][i]), "K_physical_row": int(kn["physical_row"][i])})
    return {"x0": x0, "x1": x1, "valid": valid, "naive": naive,
            "current_ask": bn["ask"], "counts": counts, "first_reason": first_reason,
            "clock_witnesses": witnesses}

def make_labels(b, ticks, current_ask):
    target = sample(b, ticks + 1000000, False, 1000000)
    known = target["valid"] & np.isfinite(current_ask) & (current_ask > 0)
    y = np.full(len(ticks), np.nan)
    y[known] = 10000 * (target["bid"][known] / current_ask[known] - 1)
    if not np.all(np.isfinite(y[known])):
        raise RuntimeError("NONFINITE_TARGET")
    return y, known

def fit_once(x, y, names):
    if len(y) == 0 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise RuntimeError("NO_FINITE_TRAINING_POPULATION")
    mean, std = x.mean(axis=0), x.std(axis=0, ddof=0)
    keep = std != 0
    design = np.column_stack((np.ones(len(y)), (x[:, keep] - mean[keep]) / std[keep]))
    assert np.all(design[:, 0] == 1)
    coef, residuals, rank, singular = np.linalg.lstsq(design, y, rcond=1e-12)
    if not np.all(np.isfinite(coef)) or not np.all(np.isfinite(singular)):
        raise RuntimeError("NONFINITE_OLS_OUTPUT")
    return {"feature_names": names, "kept_indices": np.flatnonzero(keep).tolist(),
            "removed_zero_std_names": [name for name, flag in zip(names, keep) if not flag],
            "mean": mean[keep].tolist(), "population_std": std[keep].tolist(),
            "coefficients_intercept_first": coef.tolist(), "intercept_column": "fixed_1_not_standardized",
            "rank": int(rank), "design_columns": int(design.shape[1]), "singular_values": singular.tolist(),
            "rcond": 1e-12, "fits": 1, "rows": len(y)}

def predict_fixed(x, valid, model):
    out = np.full(len(valid), np.nan)
    keep = model["kept_indices"]
    z = (x[valid][:, keep] - np.asarray(model["mean"])) / np.asarray(model["population_std"])
    design = np.column_stack((np.ones(int(valid.sum())), z))
    out[valid] = design @ np.asarray(model["coefficients_intercept_first"])
    if not np.all(np.isfinite(out[valid])):
        raise RuntimeError("NONFINITE_PREDICTION")
    return out

def bucket_summary(prediction, valid, labels, known):
    bounds = np.asarray([0, 1, 5, 10, 30, 100], dtype=float)
    indices = np.searchsorted(bounds, prediction, side="left")
    names = ["<=0", "(0,1]", "(1,5]", "(5,10]", "(10,30]", "(30,100]", ">100"]
    result = {}
    for i, name in enumerate(names):
        population = valid & (indices == i)
        scored = population & known
        actual = labels[scored]
        result[name] = {"n_predictions": int(population.sum()), "n_scored": int(scored.sum()),
                        "unknown_labels": int((population & ~known).sum()),
                        "actual_Y_mean_bp": float(actual.mean()) if len(actual) else "UNKNOWN",
                        "actual_Y_median_bp": float(np.median(actual)) if len(actual) else "UNKNOWN"}
    return result

def score_predictions(ticks, valid, predictions, y, known):
    scored = valid & known
    n = int(scored.sum())
    errors, metrics = {}, {}
    for key in ("N", "M0", "M1"):
        errors[key] = (y[scored] - predictions[key][scored]) ** 2
        if not np.all(np.isfinite(errors[key])):
            raise RuntimeError("NONFINITE_SCORING_OUTPUT")
        metrics[key] = {"MSE": float(errors[key].mean()) if n else "UNKNOWN",
                        "MAE": float(np.abs(y[scored] - predictions[key][scored]).mean()) if n else "UNKNOWN"}
    block_ids = ((ticks[scored] - day_start(CHALLENGE_DAY)) // 300000000).astype(np.int64)
    block_n = np.bincount(block_ids, minlength=288)
    contrasts, block_sums = {}, {}
    # One fixed generator/draw matrix shared by both contrasts.
    draws = np.random.Generator(np.random.PCG64(20261023)).integers(0, 288, size=(1000, 288))
    sampled_n = block_n[draws].sum(axis=1)
    for key, base in (("d0_N_minus_M1", "N"), ("d1_M0_minus_M1", "M0")):
        difference = errors[base] - errors["M1"]
        if not np.all(np.isfinite(difference)):
            raise RuntimeError("NONFINITE_ERROR_DIFFERENCE")
        sums = np.bincount(block_ids, weights=difference, minlength=288)
        block_sums[key] = sums.tolist()
        mean = float(sums.sum() / block_n.sum()) if n else "UNKNOWN"
        if np.any(sampled_n == 0):
            interval = "UNKNOWN_ZERO_BOOTSTRAP_DENOMINATOR_NO_REDRAW"
        else:
            effects = sums[draws].sum(axis=1) / sampled_n
            interval = np.percentile(effects, [2.5, 97.5], method="linear").tolist()
        contrasts[key] = {"mean_squared_error_improvement": mean, "type7_95pct_interval": interval}
    prediction_n = int(valid.sum())
    coverage = {"prediction_n": prediction_n, "fixed_grid_n": len(ticks), "scored_n": n,
                "prediction_coverage": prediction_n / len(ticks),
                "label_coverage_of_emitted": n / prediction_n if prediction_n else "UNKNOWN",
                "nonempty_5minute_blocks": int((block_n > 0).sum())}
    coverage_pass = prediction_n >= .5 * len(ticks) and prediction_n > 0 and n >= .8 * prediction_n and (block_n > 0).sum() >= 250
    error_pass = all(isinstance(x["type7_95pct_interval"], list) and x["mean_squared_error_improvement"] > 0 and x["type7_95pct_interval"][0] > 0 for x in contrasts.values())
    return {"metrics_common_label_population": metrics, "contrasts": contrasts, "coverage": coverage,
            "coverage_pass": bool(coverage_pass), "error_conditions_pass": bool(error_pass),
            "decision": "INCONCLUSIVE_COVERAGE" if not coverage_pass else ("INFORMATION_CANDIDATE_ONLY" if error_pass else "FIXED_MODEL_INCREMENT_NOT_SUPPORTED"),
            "M1_prediction_buckets_bp": bucket_summary(predictions["M1"], valid, y, known),
            "blocks": {"n": block_n.tolist(), "sum_squared_error_differences": block_sums,
                       "empty_block_effect": "UNKNOWN_NOT_ZERO", "bootstrap_repetitions": 1000,
                       "generator": "PCG64", "seed": 20261023, "percentile": "type7_linear"},
            "profitability_proven": False, "personal_arrival_conditions_proven": False}

def utc_now():
    return dt.datetime.now(dt.timezone.utc)

def read_protocol():
    path = OWNER / "protocol.json"
    if path.is_symlink() or path.stat().st_size > 65536:
        raise RuntimeError("PROTOCOL_SYMLINK_OR_SIZE_LIMIT")
    raw = path.read_bytes()
    if sha_bytes(raw) != PROTOCOL_SHA256:
        raise RuntimeError("PROTOCOL_CHANGED")
    value = json.loads(raw)
    if value["training_day"] != TRAIN_DAY or value["test_day"] != CHALLENGE_DAY:
        raise RuntimeError("FIXED_DATE_MISMATCH")
    if value["M0_features"] != M0_NAMES or value["M0_features"] + value["M1_added_features"] != M1_NAMES:
        raise RuntimeError("FIXED_FEATURE_MISMATCH")
    return value

def write_json(name, value):
    path = OUTPUT / name
    payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    ensure_output_capacity(len(payload))
    with path.open("xb") as out:
        out.write(payload)
        out.flush()
        os.fsync(out.fileno())
    return small_sha(path)

def rss_bytes():
    n = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(n if sys.platform == "darwin" else n * 1024)

def disk_bytes():
    return sum(p.stat().st_size for p in OWNER.rglob("*") if p.is_file())

def ensure_output_capacity(additional_bytes):
    if CAPS is not None and disk_bytes() + additional_bytes > CAPS["disk_bytes"] - 4194304:
        raise RuntimeError("OUTPUT_SPACE_CAP")

def check_budget():
    if CAPS is None:
        return
    if PRIOR_CPU is None or PRIOR_ACTIVE is None:
        raise RuntimeError("UNKNOWN_ACQUISITION_USAGE")
    if PRIOR_CPU + time.process_time() - RUN_CPU_START >= CAPS["cpu_seconds"]:
        raise RuntimeError("CUMULATIVE_CPU_CAP")
    if PRIOR_ACTIVE + time.monotonic() - RUN_WALL_START >= CAPS["active_seconds"]:
        raise RuntimeError("CUMULATIVE_ACTIVE_CAP")
    if rss_bytes() > CAPS["rss_bytes"]:
        raise RuntimeError("RSS_CAP")
    if disk_bytes() > CAPS["disk_bytes"] - 4194304:
        raise RuntimeError("DISK_CAP_RESERVE")

def cpu_stop(signum, frame):
    raise RuntimeError("CUMULATIVE_CPU_CAP")

def start_resource_guards():
    global WATCHDOG_THREAD
    remaining = CAPS["cpu_seconds"] - PRIOR_CPU - (time.process_time() - RUN_CPU_START)
    if remaining <= 1:
        raise RuntimeError("NO_CPU_REMAINING_BEFORE_PREFLIGHT")
    signal.signal(signal.SIGXCPU, cpu_stop)
    current = time.process_time()
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(current + remaining), math.ceil(current + remaining) + 1))
    def watch():
        while not WATCHDOG_STOP.wait(0.1):
            try:
                check_budget()
            except RuntimeError as error:
                try:
                    payload = json.dumps({"reason": error.args[0],
                        "cpu_seconds_including_acquisition": PRIOR_CPU + time.process_time() - RUN_CPU_START,
                        "peak_rss_bytes": rss_bytes(), "utc": utc_now().isoformat(), "no_retry": True}).encode("utf-8")
                    # Small emergency record uses reserved space after a resource trip.
                    with (OUTPUT / "RESOURCE_STOPPED.json").open("xb") as out:
                        out.write(payload)
                        out.flush()
                        os.fsync(out.fileno())
                finally:
                    os._exit(79)
    WATCHDOG_THREAD = threading.Thread(target=watch, name="bounded-resource-watch", daemon=True)
    WATCHDOG_THREAD.start()

def finite_nonnegative(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError("UNKNOWN_OR_INVALID_ACQUISITION_USAGE")
    if not math.isfinite(value) or value < 0:
        raise RuntimeError("UNKNOWN_OR_INVALID_ACQUISITION_USAGE")
    return float(value)

def load_receipts(protocol):
    global PRIOR_CPU, PRIOR_ACTIVE
    path = OWNER / "input-receipts.json"
    if path.is_symlink() or path.stat().st_size > 65536:
        raise RuntimeError("RECEIPT_SYMLINK_OR_SIZE_LIMIT")
    raw = path.read_bytes()
    receipt = json.loads(raw)
    files = receipt["files"]
    if not isinstance(files, list) or len(files) != 4:
        raise RuntimeError("EXACT_FOUR_ACQUISITION_RECEIPTS_REQUIRED")
    indexed = {}
    for item in files:
        name = item["filename"]
        if name in indexed or Path(name).name != name:
            raise RuntimeError("RECEIPT_DUPLICATE_OR_INVALID_NAME")
        indexed[name] = item
    if set(indexed) != {x["filename"] for x in protocol["files"]}:
        raise RuntimeError("FIXED_FILE_SET_MISMATCH")
    for spec in protocol["files"]:
        item = indexed[spec["filename"]]
        if item["url"] != spec["url"] or item["http_status"] != 200:
            raise RuntimeError("ACQUISITION_SOURCE_MISMATCH")
        observed = dt.datetime.fromisoformat(item["observed_utc"].replace("Z", "+00:00"))
        if observed.utcoffset() != dt.timedelta(0):
            raise RuntimeError("ACQUISITION_TIME_NOT_UTC")
        if isinstance(item["bytes"], bool) or not isinstance(item["bytes"], int) or item["bytes"] <= 0:
            raise RuntimeError("INVALID_ACQUISITION_BYTES")
        sha = item["sha256"]
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise RuntimeError("INVALID_ACQUISITION_SHA")
    usage = receipt["usage"]
    PRIOR_CPU = finite_nonnegative(usage["cpu_seconds"])
    PRIOR_ACTIVE = finite_nonnegative(usage["active_seconds"])
    downloads = finite_nonnegative(usage["download_bytes"])
    wait = finite_nonnegative(usage["network_wait_seconds"])
    if not sum(x["bytes"] for x in files) <= downloads <= CAPS["download_bytes"]:
        raise RuntimeError("CUMULATIVE_ACQUISITION_DOWNLOAD_CAP")
    if wait > CAPS["network_wait_seconds"]:
        raise RuntimeError("CUMULATIVE_NETWORK_WAIT_CAP")
    check_budget()
    return indexed, {"path": str(path), "sha256": sha_bytes(raw), "usage": usage}

def checked_input(spec):
    path = INPUT / spec["filename"]
    if INPUT.is_symlink() or path.is_symlink() or path.resolve().parent != INPUT.resolve():
        raise RuntimeError("INPUT_PATH_ESCAPE_OR_SYMLINK")
    return path

def preflight_one(spec, receipt):
    """Stdlib-only identity/CRC/day/field checks; no labels or statistics."""
    path = checked_input(spec)
    if path.stat().st_size != receipt["bytes"]:
        raise RuntimeError("INPUT_SIZE_MISMATCH")
    label = spec["label"]
    fields = (["bids[0].price", "asks[0].price", "bids[0].amount", "asks[0].amount"]
              if label == "B" else ["bid_price", "ask_price", "bid_amount", "ask_amount"])
    exchange, symbol = ("bitstamp", "BTCUSD") if label == "B" else ("kraken", "BTC/USD")
    start = day_start(spec["day"])
    previous = None
    rows = ties = 0
    with path.open("rb") as upstream:
        hashed = HashedStream(upstream, receipt["bytes"])
        with io.BufferedReader(hashed, buffer_size=65536) as buffered:
            with gzip.GzipFile(fileobj=buffered, mode="rb") as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="") as text:
                    reader = csv.DictReader(text)
                    names = reader.fieldnames or []
                    required = ["exchange", "symbol", "timestamp", "local_timestamp"] + fields
                    if len(names) != len(set(names)) or any(k not in names for k in required):
                        raise RuntimeError("INPUT_HEADER_ERROR")
                    for row in reader:
                        rows += 1
                        if rows % 4096 == 0:
                            check_budget()
                        if None in row or any(v is None for v in row.values()):
                            raise RuntimeError("INPUT_ROW_WIDTH_ERROR")
                        if row["exchange"] != exchange or row["symbol"] != symbol:
                            raise RuntimeError("INPUT_IDENTITY_ERROR")
                        local_text = row["local_timestamp"]
                        if not local_text.isascii() or not local_text.isdecimal():
                            raise RuntimeError("INPUT_LOCAL_TIMESTAMP_ERROR")
                        local = int(local_text)
                        if not start <= local < start + 86400000000 or (previous is not None and local < previous):
                            raise RuntimeError("INPUT_LOCAL_ORDER_OR_DAY_ERROR")
                        ties += int(local == previous)
                        previous = local
                        values = [float(row[k]) for k in fields]
                        if not all(math.isfinite(v) and v > 0 for v in values) or values[0] > values[1]:
                            raise RuntimeError("INPUT_L1_INVALID")
                    if not hashed.eof:
                        raise RuntimeError("INPUT_COMPRESSED_EOF_MISSING")
    if not rows or hashed.count != receipt["bytes"] or hashed.sha.hexdigest() != receipt["sha256"]:
        raise RuntimeError("INPUT_FINGERPRINT_ERROR")
    check_budget()
    return {"filename": spec["filename"], "role": spec["role"], "day": spec["day"],
            "bytes": hashed.count, "sha256": hashed.sha.hexdigest(), "rows": rows,
            "same_local_timestamp": ties, "gzip_crc_eof": True}

def load_role(protocol, receipts, role, day):
    pair, identities = {}, {}
    for spec in protocol["files"]:
        if spec["role"] != role:
            continue
        item = receipts[spec["filename"]]
        pair[spec["label"]], identities[spec["label"]] = read_source(
            spec["label"], checked_input(spec), item["bytes"], item["sha256"], day)
    if set(pair) != {"B", "K"}:
        raise RuntimeError("ROLE_PAIR_INCOMPLETE")
    return pair, identities

def execute_unit(protocol):
    csv.field_size_limit(1048576)
    receipts, acquisition = load_receipts(protocol)
    start_resource_guards()
    preflight = [preflight_one(spec, receipts[spec["filename"]]) for spec in protocol["files"]]
    write_json("PREFLIGHT.json", {"inputs": preflight, "acquisition": acquisition,
                                  "future_prices_not_used_to_select": True,
                                  "preflight_is_not_source_permission_or_profit_proof": True})
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    get_numpy()
    write_json("ENVIRONMENT.json", environment())
    train_pair, train_ids = load_role(protocol, receipts, "train", TRAIN_DAY)
    ticks = grid(TRAIN_DAY)
    features = make_features(train_pair["B"], train_pair["K"], ticks)
    y, known = make_labels(train_pair["B"], ticks, features["current_ask"])
    fitting = features["valid"] & known
    write_json("FIT_M0_STARTED.json", {"utc": utc_now().isoformat(), "once_only": True})
    m0 = fit_once(features["x0"][fitting], y[fitting], M0_NAMES)
    write_json("FIT_M0_COMPLETED.json", {"utc": utc_now().isoformat(), "fits": 1})
    check_budget()
    write_json("FIT_M1_STARTED.json", {"utc": utc_now().isoformat(), "once_only": True})
    m1 = fit_once(features["x1"][fitting], y[fitting], M1_NAMES)
    write_json("FIT_M1_COMPLETED.json", {"utc": utc_now().isoformat(), "fits": 1})
    check_budget()
    weights_sha = write_json("weights.json", {"protocol_sha256": PROTOCOL_SHA256,
        "training_day": TRAIN_DAY, "test_day": CHALLENGE_DAY, "models": {"M0": m0, "M1": m1},
        "source_identities": train_ids, "training_rows": int(fitting.sum()), "no_training_performance_selection": True})
    write_json("MODEL_SEALED.json", {"weights_sha256": weights_sha, "sealed_utc": utc_now().isoformat(),
        "real_fits": {"M0": 1, "M1": 1}, "historical_replay_not_pre_event_seal": True})
    del train_pair, features, y, known, fitting, m0, m1
    test_pair, test_ids = load_role(protocol, receipts, "test", CHALLENGE_DAY)
    ticks = grid(CHALLENGE_DAY)
    features = make_features(test_pair["B"], test_pair["K"], ticks)
    if small_sha(OUTPUT / "weights.json") != weights_sha:
        raise RuntimeError("MODEL_SEAL_MISMATCH")
    weights = json.loads((OUTPUT / "weights.json").read_text())
    predictions = {"N": features["naive"],
        "M0": predict_fixed(features["x0"], features["valid"], weights["models"]["M0"]),
        "M1": predict_fixed(features["x1"], features["valid"], weights["models"]["M1"])}
    check_budget()
    ensure_output_capacity(sum(x.nbytes for x in predictions.values()) + ticks.nbytes +
                           features["valid"].nbytes + features["first_reason"].nbytes + 6 * 65536)
    with (OUTPUT / "predictions.npz").open("xb") as out:
        np.savez(out, ticks=ticks, valid=features["valid"], first_reason=features["first_reason"], **predictions)
        out.flush()
        os.fsync(out.fileno())
    check_budget()
    prediction_sha = small_sha(OUTPUT / "predictions.npz")
    write_json("PREDICTIONS_SEALED.json", {"predictions_sha256": prediction_sha,
        "weights_sha256": weights_sha, "sealed_utc": utc_now().isoformat(),
        "labels_constructed": False, "raw_test_file_was_read_for_causal_replay": True,
        "source_identities": test_ids, "population": features["counts"]})
    if small_sha(OUTPUT / "predictions.npz") != prediction_sha:
        raise RuntimeError("PREDICTION_SEAL_MISMATCH")
    with np.load(OUTPUT / "predictions.npz", allow_pickle=False) as saved:
        saved_ticks, valid = saved["ticks"], saved["valid"]
        saved_predictions = {k: saved[k] for k in ("N", "M0", "M1")}
    block_ids = (saved_ticks - day_start(CHALLENGE_DAY)) // 300000000
    if not np.all((block_ids >= 0) & (block_ids < 288)):
        raise RuntimeError("TEST_BLOCK_ORIGIN_MISMATCH")
    y, known = make_labels(test_pair["B"], saved_ticks, features["current_ask"])
    check_budget()
    ensure_output_capacity(y.nbytes + known.nbytes + 2 * 65536)
    with (OUTPUT / "labels-after-prediction-seal.npz").open("xb") as out:
        np.savez(out, y=y, known=known)
        out.flush()
        os.fsync(out.fileno())
    labels_sha = small_sha(OUTPUT / "labels-after-prediction-seal.npz")
    scoring = score_predictions(saved_ticks, valid, saved_predictions, y, known)
    check_budget()
    metrics = scoring["metrics_common_label_population"]
    relative = {}
    for base in ("N", "M0"):
        base_mse, model_mse = metrics[base]["MSE"], metrics["M1"]["MSE"]
        relative[base] = (100 * (1 - model_mse / base_mse)
                          if isinstance(base_mse, (int, float)) and base_mse > 0
                          else "UNKNOWN_ZERO_OR_MISSING_BASE_MSE")
    if not scoring["coverage_pass"]:
        interpretation = "INCONCLUSIVE_COVERAGE"
    elif scoring["error_conditions_pass"]:
        interpretation = "INFORMATION_CANDIDATE_ONE_HISTORICAL_DAY_ONLY"
    elif all(isinstance(c["mean_squared_error_improvement"], (int, float)) and
             c["mean_squared_error_improvement"] > 0 for c in scoring["contrasts"].values()):
        interpretation = "POSITIVE_MEANS_BUT_INSUFFICIENT_INTERVAL_EVIDENCE"
    else:
        interpretation = "FIXED_MODEL_INCREMENT_NOT_SUPPORTED"
    if small_sha(OWNER / "input-receipts.json") != acquisition["sha256"]:
        raise RuntimeError("ACQUISITION_RECEIPTS_CHANGED")
    check_budget()
    write_json("SCORE.json", {"protocol_sha256": PROTOCOL_SHA256,
        "classification": protocol["classification"], "prediction_sha256": prediction_sha,
        "labels_sha256": labels_sha,
        "test_day": CHALLENGE_DAY, "labels_constructed_after_prediction_seal": True,
        "complete_selection_independence": protocol["complete_selection_independence"],
        "whole_market_path_unseen": protocol["whole_market_path_unseen"],
        "M1_MSE_improvement_percent_vs_baseline": relative, "interpretation": interpretation, **scoring})
    check_budget()
    return scoring["decision"]

def main():
    global RUN_CPU_START, RUN_WALL_START, CAPS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("inspect", "run"), default="inspect")
    args = parser.parse_args()
    protocol = read_protocol()
    if args.mode == "inspect":
        print(json.dumps({"status": "PREPARED_NOT_RUN", "train": TRAIN_DAY, "test": CHALLENGE_DAY,
            "registration": False, "network_requests": 0, "model_execution": False}, ensure_ascii=False))
        return 0
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise RuntimeError("EXISTING_ATTEMPT_NO_RETRY_OR_OVERWRITE")
    OUTPUT.mkdir()
    RUN_CPU_START, RUN_WALL_START = time.process_time(), time.monotonic()
    CAPS = protocol["resource_caps"]
    status = "STOPPED_NO_RETRY"
    exit_code = 2
    write_json("STARTED.json", {"utc": utc_now().isoformat(), "once_only": True,
        "protocol_sha256": PROTOCOL_SHA256, "code_sha256": small_sha(Path(__file__)),
        "historical_not_prospective": True, "network_requests": 0})
    try:
        status = execute_unit(protocol)
        check_budget()
        exit_code = 0
    except BaseException as error:
        reason = error.args[0] if isinstance(error, RuntimeError) and error.args else "NON_RUNTIME_ERROR"
        if not isinstance(reason, str) or not reason or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789" for c in reason):
            reason = "DETAIL_REDACTED"
        write_json("STOPPED.json", {"exception_class": type(error).__name__, "reason": reason,
            "utc": utc_now().isoformat(), "retry_permitted": False})
    finally:
        write_json("USAGE.json", {"cpu_seconds_this_process": time.process_time() - RUN_CPU_START,
            "acquisition_cpu_debit_seconds": PRIOR_CPU, "process_wall_seconds": time.monotonic() - RUN_WALL_START,
            "acquisition_active_debit_seconds": PRIOR_ACTIVE, "peak_rss_bytes": rss_bytes(),
            "package_disk_bytes": disk_bytes(), "status": status, "network_requests_this_process": 0,
            "download_bytes_this_process": 0, "historical_project_total_usage": "UNKNOWN"})
        try:
            if PRIOR_CPU is not None and PRIOR_ACTIVE is not None:
                check_budget()
        finally:
            WATCHDOG_STOP.set()
            if WATCHDOG_THREAD is not None:
                WATCHDOG_THREAD.join(0.2)
    print(json.dumps({"status": status, "exit_code": exit_code, "profitability_proven": False}))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
