#!/usr/bin/env python3
"""One frozen future-quote information challenge; default performs no market I/O."""
import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
import argparse
from array import array
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time

BEGIN_CPU = time.process_time()
BEGIN_WALL = time.monotonic()
OWNER = Path(__file__).resolve().parent
GOAL = OWNER.parents[2]
PLAN = OWNER.parents[1]
EXECUTION = OWNER.parent
PLAN_SHA = "82661a061a639c5ad289fa8d8f64553befaeb4d54960934da705af7ebee5ffea"
TRAIN_DAY = "2026-10-01"
CHALLENGE_DAY = "2026-11-01"
TRAIN_B = GOAL.parent / "lobframe-data-entry-20261021/bitstamp_book_snapshot_25_2026-10-01_BTCUSD.csv.gz"
TRAIN_K = GOAL / "source-pair-completion-20261023/owner/kraken_BTC-USD_quotes_2026-10-01.csv.gz.part"
TRAIN_SPECS = (("B", TRAIN_B, 26500836, "22d347447c1b12f422ea2ed16ba84725eb1b8c716a22aa6b53f775f7e2fd2fe0"),
               ("K", TRAIN_K, 12646757, "0cf04f1e284f98705f399ce7a05800ce6ffaa7b218a52921ec3776b624fc7945"))
CPU_CAP = 600
RSS_CAP = 1024 ** 3
DISK_CAP = 192 * 1024 ** 2
FREEZE_DEADLINE = dt.datetime(2026, 10, 31, 12, tzinfo=dt.timezone.utc)
FUTURE_NOT_BEFORE = dt.datetime(2026, 11, 2, 12, tzinfo=dt.timezone.utc)
M0_NAMES = ["B_log_mid_change_100ms_bp", "B_log_mid_change_500ms_bp", "B_relative_spread_bp", "B_L1_imbalance"]
M1_NAMES = M0_NAMES + ["K_log_mid_change_100ms_bp", "K_log_mid_change_500ms_bp", "log_mid_basis_minus_30_prior_anchor_mean_bp"]
np = None
AVAILABLE_CPU = None

def utc_now():
    return dt.datetime.now(dt.timezone.utc)

def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def small_sha(path):
    return sha_bytes(path.read_bytes())

def write_json(name, value):
    path = OWNER / name
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=True, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return small_sha(path)

def disk_bytes():
    return sum(p.stat().st_size for p in OWNER.rglob("*") if p.is_file())

def rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)

def prior_cpu_debit():
    start = json.loads((OWNER / "execution-start.json").read_text())
    total = start["prior_known_cpu_debit_seconds"] + start["conservative_unmetered_preparation_cpu_debit_seconds"]
    for path in OWNER.glob("usage-*.json"):
        total += json.loads(path.read_text())["cpu_seconds"]
    return total

def cpu_stop(signum, frame):
    raise RuntimeError("CUMULATIVE_CPU_CAP")

def configure_budget():
    global AVAILABLE_CPU
    AVAILABLE_CPU = CPU_CAP - prior_cpu_debit()
    if AVAILABLE_CPU <= 1:
        raise RuntimeError("CPU_ALREADY_EXHAUSTED")
    signal.signal(signal.SIGXCPU, cpu_stop)
    current = time.process_time()
    resource.setrlimit(resource.RLIMIT_CPU, (math.ceil(current + AVAILABLE_CPU), math.ceil(current + AVAILABLE_CPU) + 1))
    check_budget()

def check_budget():
    if AVAILABLE_CPU is not None and time.process_time() - BEGIN_CPU >= AVAILABLE_CPU:
        raise RuntimeError("CUMULATIVE_CPU_CAP")
    if rss_bytes() > RSS_CAP:
        raise RuntimeError("RSS_CAP")
    if disk_bytes() > DISK_CAP - 1048576:
        raise RuntimeError("DISK_CAP_RESERVE")

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

def usage(stage, status):
    value = {"stage": stage, "status": status, "completed_utc": utc_now().isoformat(),
             "pid": os.getpid(), "cpu_seconds": time.process_time() - BEGIN_CPU,
             "process_wall_seconds": time.monotonic() - BEGIN_WALL,
             "peak_rss_bytes": rss_bytes(), "owner_disk_bytes": disk_bytes(),
             "prior_cpu_debit_seconds": prior_cpu_debit(), "network_requests": 0,
             "download_bytes": 0, "historical_project_total_cpu": "UNKNOWN"}
    write_json("usage-" + stage + ".json", value)
    return value

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

def binding_release(stage):
    proposal = [p for p in PLAN.glob("*.md") if small_sha(p) == PLAN_SHA]
    if len(proposal) != 1:
        raise RuntimeError("FROZEN_PROPOSAL_MISMATCH")
    code_sha = small_sha(Path(__file__))
    release_path = EXECUTION / "root" / (stage + "-release.json")
    raw = release_path.read_bytes()
    release = json.loads(raw)
    if release.get("code_sha256") != code_sha or release.get("proposal_sha256") != PLAN_SHA:
        raise RuntimeError("ROOT_RELEASE_MISMATCH_NO_MARKET_READ")
    if release.get("environment_sha256") != small_sha(OWNER / "environment-prep.json"):
        raise RuntimeError("FROZEN_ENVIRONMENT_RELEASE_MISMATCH")
    if environment() != json.loads((OWNER / "environment-prep.json").read_text()):
        raise RuntimeError("NUMERICAL_ENVIRONMENT_CHANGED_NO_MARKET_READ")
    return {"code_sha256": code_sha, "proposal_sha256": PLAN_SHA,
            "release_sha256": sha_bytes(raw)}, release

def load_pair(specs, day):
    data, identities = {}, {}
    for label, path, size, sha in specs:
        data[label], identities[label] = read_source(label, path, size, sha, day)
    return data, identities

def train():
    binding, release = binding_release("train")
    if utc_now() >= FREEZE_DEADLINE:
        raise RuntimeError("FREEZE_DEADLINE_MISSED_NO_DATE_CHANGE")
    write_json("TRAIN_STARTED.json", {**binding, "utc": utc_now().isoformat(), "pid": os.getpid(), "once_only": True})
    get_numpy()
    csv.field_size_limit(1048576)
    pair, identities = load_pair(TRAIN_SPECS, TRAIN_DAY)
    ticks = grid(TRAIN_DAY)
    features = make_features(pair["B"], pair["K"], ticks)
    y, known = make_labels(pair["B"], ticks, features["current_ask"])
    fitting = features["valid"] & known
    # Exactly these two real lstsq calls; no performance gate, tuning or refit.
    m0 = fit_once(features["x0"][fitting], y[fitting], M0_NAMES)
    m1 = fit_once(features["x1"][fitting], y[fitting], M1_NAMES)
    check_budget()
    value = {**binding, "training_day": TRAIN_DAY, "challenge_day": CHALLENGE_DAY,
             "models": {"M0": m0, "M1": m1}, "source_identities": identities,
             "population": features["counts"], "training_label_known_in_prediction_population": int(fitting.sum()),
             "training_prediction_population_unscored_labels": int((features["valid"] & ~known).sum()),
             "clock_witnesses": features["clock_witnesses"], "training_day_already_seen_not_independent_evidence": True,
             "environment": environment(), "no_training_score_used_to_select": True}
    weights_sha = write_json("weights.json", value)
    if utc_now() >= FREEZE_DEADLINE:
        raise RuntimeError("FREEZE_DEADLINE_MISSED_AFTER_FIT_NO_RETRY")
    write_json("MODEL_SEALED.json", {**binding, "weights_sha256": weights_sha, "sealed_utc": utc_now().isoformat(),
               "deadline_utc": FREEZE_DEADLINE.isoformat(), "challenge_day": CHALLENGE_DAY,
               "M0_real_fits": 1, "M1_real_fits": 1, "cannot_claim_future_challenge_completed": True})
    return {"status": "TRAINED_ONCE_SEALED_FUTURE_PENDING", "fits": {"M0": 1, "M1": 1}, "binding": binding}

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

def future_once():
    binding, release = binding_release("future")
    if utc_now() < FUTURE_NOT_BEFORE:
        raise RuntimeError("FUTURE_INPUT_NOT_DUE_NO_MARKET_READ")
    seal = json.loads((OWNER / "MODEL_SEALED.json").read_text())
    if seal["code_sha256"] != binding["code_sha256"] or seal["proposal_sha256"] != PLAN_SHA or small_sha(OWNER / "weights.json") != seal["weights_sha256"]:
        raise RuntimeError("MODEL_SEAL_MISMATCH")
    if dt.datetime.fromisoformat(seal["sealed_utc"]) >= FREEZE_DEADLINE:
        raise RuntimeError("MODEL_NOT_SEALED_BEFORE_DEADLINE")
    # Transport is separately bounded/scheduled by Root; only these fixed files may be supplied.
    expected_paths = {"B": OWNER / "future-input/bitstamp_book_snapshot_25_2026-11-01_BTCUSD.csv.gz",
                      "K": OWNER / "future-input/kraken_quotes_2026-11-01_BTC-USD.csv.gz"}
    specs = []
    for label in ("B", "K"):
        item = release["inputs"][label]
        if item["path"] != str(expected_paths[label]):
            raise RuntimeError("FUTURE_FIXED_PATH_MISMATCH")
        specs.append((label, expected_paths[label], item["bytes"], item["sha256"]))
    if sum(item[2] for item in specs) > 128 * 1024 ** 2:
        raise RuntimeError("FUTURE_DOWNLOAD_BYTES_EXCEED_AUTHORIZED_CAP")
    write_json("FUTURE_STARTED.json", {**binding, "utc": utc_now().isoformat(), "once_only": True, "pid": os.getpid()})
    get_numpy()
    pair, identities = load_pair(specs, CHALLENGE_DAY)
    ticks = grid(CHALLENGE_DAY)
    features = make_features(pair["B"], pair["K"], ticks)
    weights = json.loads((OWNER / "weights.json").read_text())
    predictions = {"N": features["naive"], "M0": predict_fixed(features["x0"], features["valid"], weights["models"]["M0"]),
                   "M1": predict_fixed(features["x1"], features["valid"], weights["models"]["M1"])}
    # No target function is called before predictions are durably written and sealed.
    with (OWNER / "predictions.npz").open("xb") as f:
        np.savez(f, ticks=ticks, valid=features["valid"], first_reason=features["first_reason"], **predictions)
        f.flush()
        os.fsync(f.fileno())
    prediction_sha = small_sha(OWNER / "predictions.npz")
    prediction_seal_sha = write_json("PREDICTIONS_SEALED.json", {**binding, "predictions_sha256": prediction_sha,
                   "weights_sha256": seal["weights_sha256"], "sealed_utc": utc_now().isoformat(),
                   "targets_accessed": False, "population": features["counts"],
                   "source_identities": identities, "clock_witnesses": features["clock_witnesses"]})
    # Separate target connection occurs only after the durable prediction seal exists.
    if small_sha(OWNER / "predictions.npz") != prediction_sha:
        raise RuntimeError("PREDICTION_SEAL_MISMATCH")
    with np.load(OWNER / "predictions.npz", allow_pickle=False) as saved:
        saved_ticks, saved_valid = saved["ticks"], saved["valid"]
        saved_predictions = {key: saved[key] for key in ("N", "M0", "M1")}
    y, known = make_labels(pair["B"], saved_ticks, features["current_ask"])
    scoring = score_predictions(saved_ticks, saved_valid, saved_predictions, y, known)
    check_budget()
    write_json("SCORE.json", {**binding, "prediction_seal_sha256": prediction_seal_sha,
                             "targets_connected_after_prediction_seal": True, **scoring})
    return {"status": "FUTURE_ONCE_SCORED_NOT_PROFIT_PROVEN", "binding": binding, "decision": scoring["decision"]}

def synthetic_checks():
    get_numpy()
    # Physical duplicate clocks and strict past versus target-inclusive boundaries.
    source = {"local": np.asarray([100, 100, 200], dtype=np.int64),
              "bid": np.asarray([10., 11., 12.]), "ask": np.asarray([12., 13., 14.]),
              "bq": np.ones(3), "aq": np.ones(3)}
    past = sample(source, np.asarray([100, 101, 200]), True, 5000000)
    future = sample(source, np.asarray([100, 200]), False, 1000000)
    assert past["valid"].tolist() == [False, True, True]
    assert past["bid"][1:].tolist() == [11., 11.]
    assert future["bid"].tolist() == [11., 12.]
    assert np.isnan(past["bid"][0])
    # Ages: exact cap is valid; one microsecond beyond cap is not.
    assert sample(source, np.asarray([1000200, 1000201]), True, 1000000)["valid"].tolist() == [True, False]
    assert sample(source, np.asarray([5000200, 5000201]), True, 5000000)["valid"].tolist() == [True, False]
    # Two-day-shaped synthetic streams with fixed formula values, no real source.
    d = day_start(TRAIN_DAY)
    clock = np.arange(d - 1000000, d + 62000000, 50000, dtype=np.int64)
    bid = 100 + np.arange(len(clock)) * .001
    b = {"local": clock, "bid": bid, "ask": bid + .02, "bq": np.full(len(clock), 3.), "aq": np.ones(len(clock))}
    k = {"local": clock, "bid": bid * 1.001, "ask": (bid + .02) * 1.001, "bq": np.ones(len(clock)), "aq": np.ones(len(clock))}
    ticks = np.asarray([d + 60000000, d + 62000000], dtype=np.int64)
    f = make_features(b, k, ticks)
    assert bool(f["valid"][0]) and f["x0"].shape == (2, 4) and f["x1"].shape == (2, 7)
    assert abs(f["x0"][0, 3] - .5) < 1e-12
    assert abs(f["x1"][0, 6]) < 1e-10
    assert f["clock_witnesses"][0]["B_selected_local_us"] < int(ticks[0])
    assert len(grid(TRAIN_DAY)) == 43170
    # Independent prediction population survives an unavailable future label.
    valid_before = f["valid"].copy()
    y, known = make_labels(b, ticks + 100000000, f["current_ask"])
    assert np.array_equal(f["valid"], valid_before) and not known.any()
    # Synthetic OLS only: constant nonintercept column removed, intercept remains 1.
    x = np.column_stack((np.arange(6, dtype=float), np.ones(6)))
    fit = fit_once(x, 2 + 3 * x[:, 0], ["varying", "constant"])
    assert fit["removed_zero_std_names"] == ["constant"] and fit["design_columns"] == 2
    assert np.allclose(predict_fixed(x, np.ones(6, dtype=bool), fit), 2 + 3 * x[:, 0])
    # Bucket inclusions and unknown labels are based on emitted M1 predictions.
    pred = np.asarray([0., 1., 5., 10., 30., 100., 101.])
    buckets = bucket_summary(pred, np.ones(7, dtype=bool), np.arange(7, dtype=float), np.asarray([True] * 6 + [False]))
    assert all(v["n_predictions"] == 1 for v in buckets.values()) and buckets[">100"]["unknown_labels"] == 1
    # Empty 5-minute blocks retain n=0; bootstrap zero-denominator is not redrawn.
    t = np.asarray([day_start(CHALLENGE_DAY) + 60000000], dtype=np.int64)
    scoring = score_predictions(t, np.asarray([True]), {"N": np.asarray([0.]), "M0": np.asarray([0.]), "M1": np.asarray([1.])}, np.asarray([1.]), np.asarray([True]))
    assert scoring["coverage"]["nonempty_5minute_blocks"] == 1
    assert scoring["decision"] == "INCONCLUSIVE_COVERAGE"
    assert isinstance(scoring["contrasts"]["d0_N_minus_M1"]["type7_95pct_interval"], str)
    write_json("environment-prep.json", environment())
    return {"status": "SYNTHETIC_CHECKS_PASS_NO_REAL_DATA_OR_REAL_FIT", "market_files_read": 0,
            "real_fits": 0, "synthetic_OLS_fits": 1, "network_requests": 0,
            "checks": ["strict_past_and_inclusive_future_boundary", "physical_last_tie", "no_future_fill",
                       "current_1s_and_anchor_5s_edges", "M0_M1_feature_formulas", "thirty_prior_basis_anchors",
                       "43170_grid", "prediction_population_independent_of_label", "constant_removal_fixed_intercept",
                       "OLS_rcond_and_prediction_roundtrip", "M1_bucket_boundaries_and_unknowns", "empty_blocks_no_redraw"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic", "train", "future"))
    parser.add_argument("--synthetic-label", default="synthetic")
    args = parser.parse_args()
    if args.mode is None:
        print("READY_ONLY_NO_MARKET_IO")
        return 0
    configure_budget()
    stage = args.synthetic_label if args.mode == "synthetic" else args.mode
    if args.mode == "synthetic" and (not stage.startswith("synthetic") or not stage.replace("-", "").isalnum()):
        raise RuntimeError("INVALID_SYNTHETIC_RECEIPT_LABEL")
    status = "STOP_ERROR_NO_RETRY"
    try:
        if args.mode == "synthetic":
            result = synthetic_checks()
            write_json("checks-" + stage + ".json", result)
        elif args.mode == "train":
            result = train()
            write_json("train-result.json", result)
        else:
            result = future_once()
            write_json("future-result.json", result)
        status = result["status"]
        print(json.dumps(result, allow_nan=False))
        return 0
    except BaseException as error:
        write_json("failure-" + stage + ".json", {"status": status, "type": type(error).__name__,
                   "message": str(error)[:500], "utc": utc_now().isoformat(), "no_retry": True})
        print(json.dumps({"status": status, "error": type(error).__name__}))
        return 2
    finally:
        usage(stage, status)

if __name__ == "__main__":
    raise SystemExit(main())
