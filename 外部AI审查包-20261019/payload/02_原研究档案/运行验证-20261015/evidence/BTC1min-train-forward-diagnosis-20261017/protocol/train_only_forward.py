"""Independent TRAIN-only saved-weight diagnostic. No training or TEST forward."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys

PHASE = Path(__file__).resolve().parents[1]
BASE = PHASE.parents[1]
ART = PHASE / "artifacts"
AUTH = PHASE / "root/train-forward-authorization-and-fixed-scope.json"
OLD = BASE / "evidence/BTC1min-fixed-evaluation-run-20261017"
PR = BASE / "evidence/BTC1min-fixed-evaluation-readiness-20261017"
PROPOSAL = PR / "root/fixed-once-evaluation-proposal.json"
SOURCES = ["train_only_forward.py", "train_forward_supervisor.py"]
THREADS = {"OMP_NUM_THREADS": "6", "OMP_THREAD_LIMIT": "6", "OPENBLAS_NUM_THREADS": "6",
           "MKL_NUM_THREADS": "6", "VECLIB_MAXIMUM_THREADS": "6", "NUMEXPR_NUM_THREADS": "6",
           "BLIS_NUM_THREADS": "6", "PYTHONDONTWRITEBYTECODE": "1"}


def utc():
    return datetime.now(timezone.utc).isoformat()


def fp(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""):
            h.update(chunk)
    return {"sha256": h.hexdigest(), "bytes": path.stat().st_size}


def save(path, obj):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def source_inputs():
    return {str(PHASE / "protocol" / name): fp(PHASE / "protocol" / name) for name in SOURCES}


def protected_inputs():
    proposal = json.loads(PROPOSAL.read_text())
    paths = [PROPOSAL, Path(proposal["data"]["path"]),
             Path(proposal["qualification"]["train_indices_file"]),
             Path(proposal["qualification"]["test_indices_file"]),
             OLD / "artifacts/run-settings.json", OLD / "artifacts/run-scalers.json",
             OLD / "artifacts/all-model-predictions.csv", OLD / "artifacts/evaluation-results.json",
             OLD / "protocol/fixed_evaluation.py", OLD / "protocol/runtime_health.py",
             OLD / "protocol/resource_supervisor.py", OLD / "artifacts/LSTM_price.final.pt",
             OLD / "artifacts/LSTM_state.final.pt"]
    values = {str(path): fp(path) for path in paths}
    expected_proposal = "969ac08ec3504d5960b0b7787ee3204a7b6b9eb656484de22ebd4e4fb105d983"
    if values[str(PROPOSAL)]["sha256"] != expected_proposal:
        raise RuntimeError("Old frozen proposal changed")
    if values[str(Path(proposal["data"]["path"]))] != {
            "sha256": proposal["data"]["sha256"], "bytes": proposal["data"]["bytes"]}:
        raise RuntimeError("Source CSV changed")
    for split in ["train", "test"]:
        path = proposal["qualification"][split + "_indices_file"]
        if values[path]["sha256"] != proposal["qualification"][split + "_indices_sha256"]:
            raise RuntimeError("Frozen index list changed")
    seal = json.loads((OLD / "artifacts/predictions-sealed-before-scoring.json").read_text())
    for path, expected in seal["files"].items():
        if path in values and values[path] != expected:
            raise RuntimeError("Sealed old artifact changed")
    settings = json.loads((OLD / "artifacts/run-settings.json").read_text())
    for path, expected in settings["source_inputs"].items():
        if values.get(path) != expected:
            raise RuntimeError("Old source identity changed")
    for name, expected in json.loads(AUTH.read_text())["checkpoint_hashes"].items():
        if values[str(OLD / "artifacts" / name)]["sha256"] != expected:
            raise RuntimeError("Authorized checkpoint changed")
    expected_test_result = "421450f6348bc91dfb00693692605c7e779c451c6180436e74e44bd0cb071c7a"
    if values[str(OLD / "artifacts/evaluation-results.json")]["sha256"] != expected_test_result:
        raise RuntimeError("Sealed TEST results changed")
    return proposal, values


def setup_np():
    if os.environ.get("TRAIN_FORWARD_SUPERVISED_PHASE") != str(PHASE):
        raise RuntimeError("Must use new phase supervisor")
    if any(os.environ.get(k) != v for k, v in THREADS.items()) or not sys.dont_write_bytecode:
        raise RuntimeError("Thread/bytecode controls missing")
    if sys.version_info[:3] != (3, 12, 14):
        raise RuntimeError("Interpreter version mismatch")
    if datetime.now(timezone.utc) >= datetime.fromisoformat(json.loads(AUTH.read_text())["work_deadline_utc"]):
        raise RuntimeError("New diagnostic work deadline passed")
    import numpy as np
    if np.__version__ != "2.2.6" or importlib.metadata.version("torch") != "2.8.0":
        raise RuntimeError("Installed dependency version changed")
    return np


def load_train(np):
    proposal, before = protected_inputs()
    with Path(proposal["qualification"]["train_indices_file"]).open(newline="") as handle:
        declared = list(csv.DictReader(handle))
    indices = [int(x["source_row_index_zero_based"]) for x in declared]
    if len(indices) != 11950 or indices != sorted(set(indices)) or any(not 30 <= i < 13690 for i in indices):
        raise RuntimeError("Training target scope changed")
    mids, features, stamps, times = [], [], [], []
    with Path(proposal["data"]["path"]).open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        pos = {name: header.index(name) for name in
               ["system_time", "midpoint", "spread", "bids_notional_0", "asks_notional_0"]}
        if len(header) != 156:
            raise RuntimeError("Header changed")
        for i, row in enumerate(reader):
            if i > indices[-1]:
                break  # No TEST numeric records loaded or TEST input arrays built.
            if len(row) != 156 or row[0] != str(i):
                raise RuntimeError("Training source row mismatch")
            m, s, b, a = [float(row[pos[x]]) for x in
                          ["midpoint", "spread", "bids_notional_0", "asks_notional_0"]]
            if not all(math.isfinite(x) for x in [m, s, b, a]) or not (m > 0 and s >= 0 and b >= 0 and a >= 0 and b + a > 0):
                raise RuntimeError("Invalid training data")
            stamp = row[pos["system_time"]]
            dt = datetime.fromisoformat(stamp)
            if dt.utcoffset() != timedelta(0):
                raise RuntimeError("Unexpected timestamp zone")
            mids.append(m)
            features.append([m, s, (b - a) / (b + a)])
            stamps.append(stamp)
            times.append(dt)
    if len(mids) != 13690:
        raise RuntimeError("Loaded prefix changed")
    bad = [0] * len(times)
    for i in range(1, len(times)):
        bad[i] = bad[i - 1] + int(times[i] - times[i - 1] != timedelta(seconds=60))
    eligible = [i for i in range(30, 13690) if bad[i] == bad[i - 30]]
    if eligible != indices or any(x["system_time"] != stamps[i] for x, i in zip(declared, indices)):
        raise RuntimeError("Frozen training-time alignment changed")
    scaler_path = OLD / "artifacts/run-scalers.json"
    scalers = json.loads(scaler_path.read_text())
    if scalers["target_fit_indices"] != indices:
        raise RuntimeError("Saved target scaler indices changed")
    # ONLY APPLY saved means/std. No .mean(), .std(), fitting or refitting here.
    means = np.asarray(scalers["input_mean"], dtype=np.float64)
    stds = np.asarray(scalers["input_population_std"], dtype=np.float64)
    if means.shape != (3,) or stds.shape != (3,) or not np.isfinite(means).all() or not np.isfinite(stds).all():
        raise RuntimeError("Invalid saved scaler")
    if any(stds < 0) or list(stds == 0) != scalers["constant_input_channels"]:
        raise RuntimeError("Constant-channel metadata mismatch")
    target_mean, target_std = scalers["target_mean"], scalers["target_population_std"]
    if not (math.isfinite(target_mean) and math.isfinite(target_std) and target_std > 0):
        raise RuntimeError("Invalid fixed target scaler")
    raw = np.asarray(features, dtype=np.float64)
    standardized = np.zeros_like(raw)
    active = stds > 0
    standardized[:, active] = (raw[:, active] - means[active]) / stds[active]
    inputs = np.stack([standardized[i - 30:i] for i in indices])
    if inputs.shape != (11950, 30, 3) or not np.isfinite(inputs).all():
        raise RuntimeError("TRAIN array shape/finiteness invalid")
    for k in [0, len(indices) - 1]:
        i = indices[k]
        if not np.array_equal(inputs[k], standardized[i - 30:i]):
            raise RuntimeError("Training input alignment failed")
    price = inputs.copy()
    price[:, :, 2] = 0
    if not np.array_equal(price[:, :, :2], inputs[:, :, :2]) or not (price[:, :, 2] == 0).all():
        raise RuntimeError("Matched ablation failed")
    return {"indices": indices, "mids": mids, "stamps": stamps, "inputs": inputs,
            "scalers": scalers, "before": before}


def check_unchanged(before):
    _, after = protected_inputs()
    if after != before:
        raise RuntimeError("A protected original changed")
    return after


def preflight(np):
    data = load_train(np)
    save(ART / "preflight.json", {
        "status": "PASS_TRAIN_ONLY_NONMODEL_PREFLIGHT_STOP_BEFORE_MODEL_CONSTRUCTION",
        "at_utc": utc(), "source_inputs": source_inputs(),
        "protected_originals_before": data["before"],
        "protected_originals_after": check_unchanged(data["before"]),
        "TRAIN_input_array_shape": list(data["inputs"].shape),
        "TRAIN_source_prefix_rows_loaded": len(data["mids"]),
        "loaded_numeric_source_index_max": 13689,
        "target_count": len(data["indices"]),
        "saved_scalers_applied_without_refit": True,
        "train_boundary_and_all_timestamps_match": True,
        "same_shape_third_channel_zero_ablation_checked": True,
        "python": sys.version, "numpy": np.__version__,
        "torch_metadata_only_not_imported": importlib.metadata.version("torch"),
        "TEST_arrays_or_targets_constructed": 0,
        "model_construction_parameter_load_forward_predictions": 0,
        "next": "Wait for independent root source-review gate before ONE train-only forward"})
    print("PASS_TRAIN_ONLY_PREFLIGHT_NO_MODEL_CONSTRUCTION", flush=True)


def gate(path):
    if path is None or Path(path).resolve().parent != (PHASE / "root").resolve():
        raise RuntimeError("Root-owned independent source gate required")
    review = json.loads(Path(path).read_text())
    if not str(review.get("status", "")).startswith("PASS") or review.get("allow_train_forward") is not True:
        raise RuntimeError("Train-only forward has not been independently approved")
    if review.get("source_inputs") != source_inputs() or review.get("authorization_sha256") != fp(AUTH)["sha256"]:
        raise RuntimeError("Source/authorization gate mismatch")
    if json.loads((ART / "preflight.json").read_text())["source_inputs"] != source_inputs():
        raise RuntimeError("Source changed after preflight")
    return {"path": str(Path(path).resolve()), **fp(Path(path))}


def tensor_hash(items):
    h = hashlib.sha256()
    for name, tensor in sorted(items):
        array = tensor.detach().cpu().numpy()
        h.update(json.dumps({"name": name, "shape": list(array.shape), "dtype": str(array.dtype)}, sort_keys=True).encode())
        h.update(array.tobytes(order="C"))
    return h.hexdigest()


def forward_only(np, approval):
    approved = gate(approval)
    save(ART / "forward.single-use-claim.json", {"at_utc": utc(), "gate": approved,
         "stage": "ONE_EVAL_PASS_EACH_MODEL_ALL11950_TRAIN_WINDOWS_NO_RETRY"})
    data = load_train(np)
    import torch
    if torch.__version__ != "2.8.0":
        raise RuntimeError("Actual Torch version changed")
    torch.set_num_threads(6)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    if not torch.are_deterministic_algorithms_enabled():
        raise RuntimeError("Determinism request failed")
    class SavedLSTM(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = torch.nn.LSTM(3, 16, num_layers=1, bias=True, batch_first=True,
                                      dropout=0, bidirectional=False, proj_size=0,
                                      device="cpu", dtype=torch.float32)
            self.head = torch.nn.Linear(16, 1, bias=True, device="cpu", dtype=torch.float32)

        def forward(self, x):
            hidden, _ = self.lstm(x)  # Default zero state for each independent window.
            return self.head(hidden[:, -1, :]).squeeze(-1)
    preds, model_receipts = {}, {}
    for name in ["LSTM_price", "LSTM_state"]:
        path = OLD / "artifacts" / (name + ".final.pt")
        saved = torch.load(path, weights_only=True, map_location="cpu")
        model = SavedLSTM()
        model.load_state_dict(saved["state_dict"], strict=True)
        model.requires_grad_(False)
        model.eval()
        before = tensor_hash(model.named_parameters())
        if before != tensor_hash(saved["state_dict"].items()):
            raise RuntimeError("Loaded parameter bytes differ from checkpoint")
        features = data["inputs"].copy()
        if name == "LSTM_price":
            features[:, :, 2] = 0
        x = torch.from_numpy(features.astype(np.float32))
        chunks = []
        with torch.no_grad():
            for start in range(0, len(x), 64):
                chunks.append(model(x[start:start + 64]).cpu().numpy().astype(np.float64))
        scaled = np.concatenate(chunks)
        pred = scaled * data["scalers"]["target_population_std"] + data["scalers"]["target_mean"]
        if pred.shape != (11950,) or not np.isfinite(pred).all():
            raise RuntimeError("Invalid TRAIN predictions; no repeat")
        after = tensor_hash(model.named_parameters())
        if after != before:
            raise RuntimeError("Weights changed during eval")
        preds[name] = pred
        model_receipts[name] = {"checkpoint": {"path": str(path), **fp(path)},
                               "loaded_state_sha256": before, "after_eval_state_sha256": after,
                               "strict_load": True, "eval_mode": not model.training,
                               "samples": len(x), "batch_size": 64,
                               "batch_count": len(chunks), "parameter_updates": 0}
        del model, saved, x, features
    output = ART / "all-TRAIN-predictions.csv"
    with output.open("x", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["source_index", "system_time", "actual_mid", "last_known_mid",
                         "LSTM_price", "LSTM_state", "unchanged_price"])
        for k, i in enumerate(data["indices"]):
            writer.writerow([i, data["stamps"][i], repr(data["mids"][i]), repr(data["mids"][i - 1]),
                             repr(float(preds["LSTM_price"][k])), repr(float(preds["LSTM_state"][k])),
                             repr(data["mids"][i - 1])])
        handle.flush()
        os.fsync(handle.fileno())
    settings = {"at_utc": utc(), "source_inputs": source_inputs(), "approval": approved,
                "authorization": {"path": str(AUTH), **fp(AUTH)},
                "protected_originals_before": data["before"],
                "protected_originals_after": check_unchanged(data["before"]),
                "model_receipts": model_receipts,
                "python": sys.version, "numpy": np.__version__, "torch": torch.__version__,
                "threads": [torch.get_num_threads(), torch.get_num_interop_threads()],
                "deterministic": torch.are_deterministic_algorithms_enabled(),
                "dtype": "CPU float32 forward, float64 saved inverse-scale predictions",
                "TEST_forward_model_training_backward_optimizer": 0,
                "scalers_applied_from_original_unchanged": True}
    settings_path = ART / "train-forward-settings.json"
    save(settings_path, settings)
    save(ART / "TRAIN-predictions-sealed-before-summary.json", {
        "status": "ALL11950_TRAIN_PREDICTIONS_SAVED_NO_AGGREGATE_METRICS_YET",
        "at_utc": utc(), "files": {str(output): fp(output), str(settings_path): fp(settings_path)}})
    print("PASS_SINGLE_TRAIN_FORWARD_SEALED_BEFORE_SUMMARY", flush=True)


def summarize(approval):
    approved = gate(approval)
    sealpath = ART / "TRAIN-predictions-sealed-before-summary.json"
    sealed = json.loads(sealpath.read_text())
    for path, expected in sealed["files"].items():
        if fp(path) != expected:
            raise RuntimeError("New TRAIN seal changed")
    save(ART / "summary.single-use-claim.json", {"at_utc": utc(), "approval": approved})
    _, before = protected_inputs()
    with (ART / "all-TRAIN-predictions.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 11950:
        raise RuntimeError("Incomplete TRAIN output")
    results = {}
    for name in ["LSTM_price", "LSTM_state", "unchanged_price"]:
        errors, raw = [], []
        for row in rows:
            difference = float(row[name]) - float(row["actual_mid"])
            errors.append(difference / float(row["last_known_mid"]))
            raw.append(difference)
        mse = math.fsum(x * x for x in errors) / len(errors)
        results[name] = {"count": len(rows), "relative_MSE": mse,
                         "MAE_basis_points": math.fsum(abs(x) for x in errors) / len(errors) * 10000,
                         "RMSE_basis_points": math.sqrt(mse) * 10000,
                         "signed_error_bias_basis_points": math.fsum(errors) / len(errors) * 10000,
                         "raw_price_RMSE": math.sqrt(math.fsum(x * x for x in raw) / len(raw))}
    target_std = json.loads((OLD / "artifacts/run-scalers.json").read_text())["target_population_std"]
    prior_test = json.loads((OLD / "artifacts/evaluation-results.json").read_text())
    comparison = {}
    for name in ["LSTM_price", "LSTM_state"]:
        comparison[name] = {
            "TRAIN_relative_MSE_ratio_to_same_TRAIN_persistence": results[name]["relative_MSE"] / results["unchanged_price"]["relative_MSE"],
            "TRAIN_MSE_strictly_below_same_TRAIN_persistence": results[name]["relative_MSE"] < results["unchanged_price"]["relative_MSE"],
            "TRAIN_raw_price_RMSE_over_saved_TRAIN_target_std": results[name]["raw_price_RMSE"] / target_std,
            "TEST_metrics_read_only_from_prior_seal_no_recalculation": prior_test["results"][name],
            "TEST_MSE_ratio_to_same_TEST_persistence": prior_test["results"][name]["MSE"] / prior_test["results"]["unchanged_price"]["MSE"],
            "interpretation": ("TRAIN beats persistence while TEST is worse: generalization gap, not unique overfit proof."
                               if results[name]["relative_MSE"] < results["unchanged_price"]["relative_MSE"]
                               else "Minute-scale precision not demonstrated even on TRAIN; not proof of no coarse price tracking or all AI failure.")}
    save(ART / "train-forward-diagnostic-summary.json", {
        "status": "COMPLETED_SINGLE_SAVED_WEIGHT_TRAIN_DIAGNOSIS_NOT_NEW_OOS",
        "at_utc": utc(), "TRAIN_results": results, "comparison": comparison,
        "saved_TRAIN_target_std_not_refit": target_std,
        "TEST_persistence_metrics_read_only": prior_test["results"]["unchanged_price"],
        "prior_TEST_result": {"path": str(OLD / "artifacts/evaluation-results.json"),
                              **fp(OLD / "artifacts/evaluation-results.json")},
        "TRAIN_prediction_seal": {"path": str(sealpath), **fp(sealpath)},
        "protected_originals_before": before, "protected_originals_after": check_unchanged(before),
        "no_new_threshold_no_learning_curve_recovery_no_validation_set": True,
        "not_profit_or_capacity_or_new_unseen_evaluation": True})
    print("PASS_TRAIN_SUMMARY_COMPLETE_ORIGINAL_TEST_NOT_RERUN", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["preflight", "forward", "summary"])
    parser.add_argument("--approval", default=None)
    args = parser.parse_args()
    if args.stage == "summary":
        # No NumPy/Torch import needed for arithmetic on sealed TRAIN output.
        if os.environ.get("TRAIN_FORWARD_SUPERVISED_PHASE") != str(PHASE):
            raise RuntimeError("Must use new supervisor")
        summarize(args.approval)
    else:
        np = setup_np()
        if args.stage == "preflight":
            preflight(np)
        else:
            forward_only(np, args.approval)


if __name__ == "__main__":
    main()
