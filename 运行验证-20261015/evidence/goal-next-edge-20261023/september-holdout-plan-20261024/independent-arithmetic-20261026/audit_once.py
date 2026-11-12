"""One authorized scalar audit; never fit, label, score, or replace predictions."""
import ast
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
import sys
import threading
import time
from array import array

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "prepared-20261024"
OWNER = BASE / "owner"
OLD = OWNER / "output"
START_CPU = time.process_time()
START_WALL = time.monotonic()
STOP = threading.Event()
NEW_FILES = [HERE / "STARTED.json", HERE / "result.json"]

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def peak():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)

def check_budget():
    if time.process_time() - START_CPU >= 300:
        raise RuntimeError("CPU_CAP")
    if time.monotonic() - START_WALL >= 3600:
        raise RuntimeError("ACTIVE_CAP")
    if peak() >= 512 * 1024**2:
        raise RuntimeError("MEMORY_CAP")
    if sum(f.stat().st_size for f in HERE.iterdir() if f.is_file()) >= 16 * 1024**2:
        raise RuntimeError("DISK_CAP")

def write(name, data):
    with (HERE / name).open("x") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)

def watchdog():
    while not STOP.wait(.1):
        try:
            check_budget()
        except Exception as exc:
            try:
                write("RESOURCE_STOPPED.json", {"status": "INCONCLUSIVE_RESOURCE_STOP", "reason": str(exc)})
            finally:
                os._exit(79)

def run():
    # An exclusive marker makes this an at-most-once formal invocation.
    write("STARTED.json", {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "pid": os.getpid(), "scope": "scalar arithmetic audit only"})
    resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
    worker = threading.Thread(target=watchdog, daemon=True)
    worker.start()
    result = {"status": "INCONCLUSIVE", "no_fit": True, "no_labels_read": True,
              "no_scoring": True, "no_original_matmul_replay": True,
              "new_files": [str(x) for x in NEW_FILES]}
    before = {}
    try:
        release = json.loads((BASE / "root/execution-release.json").read_text())
        source = OWNER / "september_challenge.py"
        if sha(source) != release["model_code_sha256"]:
            raise RuntimeError("CODE_IDENTITY_MISMATCH")
        if sha(OWNER / "protocol.json") != release["protocol_sha256"]:
            raise RuntimeError("PROTOCOL_IDENTITY_MISMATCH")
        weights = json.loads((OLD / "weights.json").read_text())
        model_seal = json.loads((OLD / "MODEL_SEALED.json").read_text())
        pred_seal = json.loads((OLD / "PREDICTIONS_SEALED.json").read_text())
        if sha(OLD / "weights.json") != model_seal["weights_sha256"] or model_seal["weights_sha256"] != pred_seal["weights_sha256"]:
            raise RuntimeError("WEIGHTS_IDENTITY_MISMATCH")
        if sha(OLD / "predictions.npz") != pred_seal["predictions_sha256"]:
            raise RuntimeError("PREDICTIONS_IDENTITY_MISMATCH")
        protected = [source, OWNER / "protocol.json", OLD / "weights.json", OLD / "predictions.npz", OLD / "SCORE.json", OLD / "MODEL_SEALED.json", OLD / "PREDICTIONS_SEALED.json"]
        before = {str(f): sha(f) for f in protected}
        # Execute only the specified existing causal input definitions, never the
        # original module's top-level business entry, fit, prediction, or scoring.
        allowed = {"get_numpy", "day_start", "grid", "HashedStream", "read_source", "sample", "make_features"}
        tree = ast.parse(source.read_text())
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in allowed]
        if {n.name for n in nodes} != allowed:
            raise RuntimeError("EXTRACTION_INCOMPLETE")
        space = dict(globals(), np=None)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), space)
        import numpy as np
        with np.load(OLD / "predictions.npz", allow_pickle=False) as sealed:
            saved = {k: sealed[k] for k in ("ticks", "valid", "first_reason", "N", "M0", "M1")}
        specs = {k: v for k, v in pred_seal["source_identities"].items()}
        sources = {}
        for key in ("B", "K"):
            spec = specs[key]
            path = OWNER / "input" / Path(spec["path"]).name
            sources[key], identity = space["read_source"](key, path, spec["bytes"], spec["sha256"], "2026-09-03")
            before[str(path)] = identity["sha256"]
        ticks = space["grid"]("2026-09-03")
        features = space["make_features"](sources["B"], sources["K"], ticks)
        alignment = {"ticks": bool(np.array_equal(ticks, saved["ticks"])),
                     "valid": bool(np.array_equal(features["valid"], saved["valid"])),
                     "first_reason": bool(np.array_equal(features["first_reason"], saved["first_reason"])),
                     "valid_count": int(features["valid"].sum())}
        result["alignment"] = alignment
        if not all(alignment[k] for k in ("ticks", "valid", "first_reason")) or alignment["valid_count"] != 35115:
            raise RuntimeError("INPUT_ALIGNMENT_FAILED")
        result["models"] = {}
        indices = np.flatnonzero(saved["valid"])
        for name, feature_name in (("M0", "x0"), ("M1", "x1")):
            model = weights["models"][name]
            matrix = features[feature_name]
            coef = model["coefficients_intercept_first"]
            total_difference = []
            max_abs, max_ratio, worst = -1.0, -1.0, None
            exceed = nonfinite = 0
            first_bad = None
            for count, index in enumerate(indices):
                if count % 4096 == 0:
                    check_budget()
                terms = [float(coef[0])]
                for j, column in enumerate(model["kept_indices"]):
                    raw = float(matrix[index, column])
                    z = (raw - float(model["mean"][j])) / float(model["population_std"][j])
                    term = z * float(coef[j + 1])
                    if not all(math.isfinite(t) for t in (raw, z, term)):
                        nonfinite += 1
                        raise RuntimeError("NONFINITE_INDEPENDENT_TERMS")
                    terms.append(term)
                reference = math.fsum(terms)
                old = float(saved[name][index])
                if not math.isfinite(reference) or not math.isfinite(old):
                    nonfinite += 1
                    raise RuntimeError("NONFINITE_OUTPUT")
                difference = abs(reference - old)
                tolerance = 1e-10 + 64 * 2.220446049250313e-16 * math.fsum(abs(t) for t in terms)
                total_difference.append(difference)
                max_ratio = max(max_ratio, difference / tolerance)
                witness = {"grid_index": int(index), "tick_us": int(ticks[index]), "sealed_bp": old,
                           "scalar_bp": reference, "absolute_difference_bp": difference, "tolerance_bp": tolerance}
                if difference > max_abs:
                    max_abs, worst = difference, witness
                if difference > tolerance:
                    exceed += 1
                    if first_bad is None:
                        first_bad = witness
            result["models"][name] = {"compared": len(indices), "nonfinite": nonfinite,
                "over_tolerance": exceed, "maximum_absolute_difference_bp": max_abs,
                "mean_absolute_difference_bp": math.fsum(total_difference) / len(indices),
                "maximum_difference_over_tolerance_ratio": max_ratio, "worst": worst,
                "first_over_tolerance": first_bad}
        check_budget()
        result["status"] = "PASS_ALL_SCALAR_RESULTS_WITHIN_FIXED_TOLERANCE" if all(v["over_tolerance"] == 0 for v in result["models"].values()) else "FAIL_PREDICTION_NUMERICAL_RELIABILITY"
    except Exception as exc:
        result["reason"] = type(exc).__name__ + ":" + str(exc)
    finally:
        result["original_hashes_before"] = before
        after = {path: sha(Path(path)) for path in before}
        result["original_hashes_after"] = after
        result["originals_unchanged"] = before == after
        if not result["originals_unchanged"]:
            result["status"] = "INCONCLUSIVE_ORIGINAL_CHANGED"
        result["cpu_seconds"] = time.process_time() - START_CPU
        result["wall_seconds"] = time.monotonic() - START_WALL
        result["peak_rss_bytes"] = peak()
        result["actual_blas_threads"] = "UNKNOWN; no BLAS operation invoked by the scalar reference"
        result["requested_numeric_threads"] = 1
        result["spend_usd"] = result["download_bytes"] = 0
        result["warning_root_cause"] = "UNKNOWN; original matmul not invoked"
        result["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        check_budget()
        write("result.json", result)
        STOP.set()
        worker.join(timeout=1)
    print(json.dumps({"status": result["status"], "models": result.get("models"), "reason": result.get("reason")}, ensure_ascii=False))

if __name__ == "__main__":
    run()
