"""Independent single-run adapter for the frozen BTC1min proposal.

preflight never fits a model or produces test predictions. fit_predict and score
are separate, single-use, root-reviewed gates. No author source is executed.
"""
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

# -I removes script-directory imports. Restore ONLY this owned source directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime_health import (
    ART, BASE, EXPECTED_PROPOSAL, PHASE, PROPOSAL,
    fingerprint, health, utc, write_new_json,
)

SOURCE_NAMES = ["fixed_evaluation.py", "runtime_health.py", "resource_supervisor.py"]
VARIANTS = ["LSTM_price", "LSTM_state", "Ridge_price", "Ridge_state"]


def source_manifest():
    return {str(PHASE / "protocol" / name): fingerprint(PHASE / "protocol" / name)
            for name in SOURCE_NAMES}


def require_supervision():
    # The supervisor issues an exact PID-scoped launch receipt before starting us.
    if os.environ.get("BTC_FIXED_SUPERVISED_PHASE") != str(PHASE):
        raise RuntimeError("Use the owned synchronous resource supervisor")


def root_gate(path):
    if path is None:
        raise RuntimeError("Independent root source-review approval required before fitting/scoring")
    path = Path(path).resolve()
    if path.parent != (PHASE / "root").resolve():
        raise RuntimeError("Approval must be an existing root-owned receipt in this phase")
    gate = json.loads(path.read_text())
    if not str(gate.get("status", "")).startswith("PASS") or gate.get("allow_training") is not True:
        raise RuntimeError("Root review has not approved this single fixed run")
    if gate.get("proposal_sha256") != EXPECTED_PROPOSAL:
        raise RuntimeError("Root review proposal binding mismatch")
    if gate.get("source_inputs") != source_manifest():
        raise RuntimeError("Current adapter source differs from independently approved source")
    return {"path": str(path), **fingerprint(path)}


def claim_once(name):
    # Retained even on failure: never silently repeat a real fit/prediction pass.
    write_new_json(ART / (name + ".single-use-claim.json"),
                   {"stage": name, "at_utc": utc(), "source_inputs": source_manifest()})


def time_bad_prefix(times):
    prefix = [0] * len(times)
    for i in range(1, len(times)):
        prefix[i] = prefix[i - 1] + int(times[i] - times[i - 1] != timedelta(seconds=60))
    return prefix


def unique_history_rows(np, indices, window, length):
    mask = np.zeros(length, dtype=bool)
    for i in indices:
        mask[int(i) - window:int(i)] = True
    return np.flatnonzero(mask)


def standardize(np, values, mean, std):
    result = np.zeros_like(values, dtype=np.float64)
    active = std > 0
    result[:, active] = (values[:, active] - mean[active]) / std[active]
    return result


def make_inputs(np, scaled, indices, window):
    return np.stack([scaled[int(i) - window:int(i)] for i in indices], axis=0)


def load_data(np):
    proposal = json.loads(PROPOSAL.read_text())
    paths = {"proposal": PROPOSAL, "CSV": Path(proposal["data"]["path"])}
    if fingerprint(paths["CSV"]) != {"sha256": proposal["data"]["sha256"],
                                    "bytes": proposal["data"]["bytes"]}:
        raise RuntimeError("Frozen CSV bytes/hash mismatch")
    rows, strings, times = [], [], []
    selected = ["midpoint", "spread", "bids_notional_0", "asks_notional_0"]
    with paths["CSV"].open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(header) != 156 or len(set(header)) != 156:
            raise RuntimeError("CSV header format mismatch")
        positions = [header.index(x) for x in selected]
        ti = header.index("system_time")
        for number, row in enumerate(reader):
            if len(row) != len(header) or row[0] != str(number):
                raise RuntimeError("CSV row width/source index changed")
            rows.append([float(row[j]) for j in positions])
            strings.append(row[ti])
            stamp = datetime.fromisoformat(row[ti])
            if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
                raise RuntimeError("Timestamp timezone mismatch")
            times.append(stamp)
    values = np.asarray(rows, dtype=np.float64)
    if values.shape != (17113, 4) or not np.isfinite(values).all():
        raise RuntimeError("CSV numeric dimensions/finiteness changed")
    mid, spread, bid, ask = values.T
    if not ((mid > 0).all() and (spread >= 0).all() and (bid >= 0).all()
            and (ask >= 0).all() and ((bid + ask) > 0).all()):
        raise RuntimeError("New invalid numeric field; no silent exclusion")
    if any(times[i] <= times[i - 1] for i in range(1, len(times))):
        raise RuntimeError("Timestamp sequence changed")
    window, cut = proposal["qualification"]["W"], proposal["qualification"]["T"]
    if window != 30 or cut != 13690 or len(times) != proposal["data"]["rows"]:
        raise RuntimeError("Frozen split changed")
    prefix = time_bad_prefix(times)
    indices = {}
    for split, candidates in [("train", range(window, cut)),
                              ("test", range(cut + 31, len(times)))]:
        path = Path(proposal["qualification"][split + "_indices_file"])
        if fingerprint(path)["sha256"] != proposal["qualification"][split + "_indices_sha256"]:
            raise RuntimeError("Frozen index-list hash changed")
        paths[split + "_indices"] = path
        with path.open(newline="") as handle:
            pairs = list(csv.DictReader(handle))
        fixed = [int(x["source_row_index_zero_based"]) for x in pairs]
        derived = [i for i in candidates if prefix[i] - prefix[i - window] == 0]
        if fixed != derived or len(fixed) != proposal["qualification"][split + "_count"]:
            raise RuntimeError("Time qualification differs from frozen full list")
        if any(x["system_time"] != strings[i] for x, i in zip(pairs, fixed)):
            raise RuntimeError("Index timestamp binding changed")
        indices[split] = np.asarray(fixed, dtype=np.int64)
    dates = {}
    for i in indices["test"]:
        date = times[int(i)].date().isoformat()
        dates[date] = dates.get(date, 0) + 1
    if dates != proposal["qualification"]["test_partial_utc_dates"]:
        raise RuntimeError("Frozen date coverage changed")
    features = np.column_stack([mid, spread, (bid - ask) / (bid + ask)])
    history = unique_history_rows(np, indices["train"], window, len(times))
    means = features[history].mean(axis=0, dtype=np.float64)
    stds = features[history].std(axis=0, ddof=0, dtype=np.float64)
    target_mean = float(mid[indices["train"]].mean(dtype=np.float64))
    target_std = float(mid[indices["train"]].std(ddof=0, dtype=np.float64))
    if target_std <= 0 or not np.isfinite(target_std):
        raise RuntimeError("Invalid/constant TRAIN target scale")
    scaled = standardize(np, features, means, stds)
    xtrain = make_inputs(np, scaled, indices["train"], window)
    xtest = make_inputs(np, scaled, indices["test"], window)
    ytrain = (mid[indices["train"]] - target_mean) / target_std
    if xtrain.shape != (11950, 30, 3) or xtest.shape != (2972, 30, 3):
        raise RuntimeError("Input shape mismatch")
    if not all(np.isfinite(x).all() for x in [features, scaled, xtrain, xtest, ytrain]):
        raise RuntimeError("Nonfinite scaled inputs")
    scalers = {"input_channel_order": ["midpoint", "spread", "I0"],
               "input_mean": means.tolist(), "input_population_std": stds.tolist(),
               "constant_input_channels": (stds == 0).tolist(),
               "input_fit_rows": history.tolist(), "input_fit_row_count": len(history),
               "target_mean": target_mean, "target_population_std": target_std,
               "target_fit_indices": indices["train"].tolist(),
               "test_fitting": False, "sample_weighting": "unique TRAIN input source rows, not repeated overlapping slots"}
    data = {"proposal": proposal, "input_paths": paths, "mid": mid,
            "timestamps": strings, "times": times, "indices": indices,
            "features": features, "scaled": scaled, "history": history,
            "xtrain": xtrain, "xtest": xtest, "ytrain": ytrain,
            "scalers": scalers, "dates": dates}
    return data


def parameter_hash(model):
    digest = hashlib.sha256()
    descriptions = []
    for name, tensor in sorted(model.named_parameters()):
        array = tensor.detach().cpu().numpy()
        description = {"name": name, "shape": list(array.shape), "dtype": str(array.dtype)}
        digest.update(json.dumps(description, sort_keys=True).encode())
        digest.update(array.tobytes(order="C"))
        descriptions.append(description)
    return {"sha256": digest.hexdigest(), "parameters": descriptions,
            "hash_encoding": "sorted names; sorted-key JSON descriptor then contiguous C-order CPU tensor bytes"}


def fresh_model(torch):
    class SmallLSTM(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = torch.nn.LSTM(3, 16, num_layers=1, bias=True, batch_first=True,
                                      dropout=0, bidirectional=False, proj_size=0,
                                      device="cpu", dtype=torch.float32)
            self.head = torch.nn.Linear(16, 1, bias=True, device="cpu", dtype=torch.float32)

        def forward(self, x):
            output, _ = self.lstm(x)  # no supplied state: fresh zero h/c per window
            return self.head(output[:, -1, :]).squeeze(-1)
    model = SmallLSTM()
    # Constructor defaults consume RNG; reseed immediately before ALL explicit initialization.
    torch.random.default_generator.manual_seed(20261017)
    with torch.no_grad():
        for _, tensor in sorted(model.named_parameters()):
            tensor.uniform_(-0.25, 0.25)
    return model


def hand_checks(np, data):
    # Tiny hand-verifiable arrays only; no fit or model forward.
    toy = np.arange(40 * 3, dtype=np.float64).reshape(40, 3)
    windows = make_inputs(np, toy, [30, 31], 30)
    assert np.array_equal(windows[0], toy[0:30])
    assert np.array_equal(windows[1], toy[1:31])
    assert np.array_equal(unique_history_rows(np, [3, 4], 3, 10), [0, 1, 2, 3])
    basic = np.asarray([[1.0, 7.0], [3.0, 7.0]], dtype=np.float64)
    mu, sd = basic.mean(axis=0), basic.std(axis=0, ddof=0)
    assert np.array_equal(standardize(np, basic, mu, sd), [[-1.0, 0.0], [1.0, 0.0]])
    assert np.array_equal(standardize(np, np.asarray([[5.0, 99.0]]), mu, sd), [[3.0, 0.0]])
    assert np.allclose(np.linalg.solve([[2.0, 0.0], [0.0, 4.0]], [6.0, 8.0]), [3.0, 2.0])
    cut = 13690
    assert int(data["indices"]["train"].max()) < cut
    assert int(data["indices"]["test"].min()) == cut + 31
    assert data["history"].max() < cut
    assert data["history"].max() < int(data["indices"]["test"].min()) - 30
    for split in ["train", "test"]:
        for k in [0, len(data["indices"][split]) - 1]:
            i = int(data["indices"][split][k])
            assert np.array_equal(data["x" + split][k], data["scaled"][i - 30:i])
    price = data["xtrain"].copy()
    price[:, :, 2] = 0
    assert np.array_equal(price[:, :, :2], data["xtrain"][:, :, :2])
    assert (price[:, :, 2] == 0).all()
    return {"toy_alignment": True, "unique_row_scaler_weighting": True,
            "train_only_scale_and_constant_channel_policy": True,
            "tiny_linear_equation_not_model_fit": True,
            "actual_boundary_input_alignment": True,
            "same_shape_I0_ablation": True, "all_without_model_forward": True}


def preflight(np, torch, health_receipt):
    data = load_data(np)
    checks = hand_checks(np, data)
    first, second = fresh_model(torch), fresh_model(torch)
    hash1, hash2 = parameter_hash(first), parameter_hash(second)
    if hash1 != hash2:
        raise RuntimeError("Matched model initialization mismatch")
    write_new_json(ART / "preflight-health.json", health_receipt)
    write_new_json(ART / "preflight-scalers.json", data["scalers"])
    write_new_json(ART / "preflight-initial-parameter-reference.json", hash1)
    receipt = {"status": "PASS_NONTRAINING_PREFLIGHT_STOP_BEFORE_ANY_FIT",
               "at_utc": utc(), "source_inputs": source_manifest(),
               "frozen_inputs": {str(x): fingerprint(x) for x in data["input_paths"].values()},
               "train_shape": list(data["xtrain"].shape), "test_shape": list(data["xtest"].shape),
               "train_count": 11950, "test_count": 2972,
               "test_partial_dates": data["dates"], "checks": checks,
               "scalers_receipt": fingerprint(ART / "preflight-scalers.json"),
               "matched_initial_parameter_hash": hash1["sha256"],
               "model_initialization_only": True, "model_forward_fit_predictions_scoring": 0,
               "state": "STOPPED_FOR_INDEPENDENT_ROOT_SOURCE_REVIEW_BEFORE_FITTING"}
    write_new_json(ART / "preflight-result.json", receipt)
    print(json.dumps({"status": receipt["status"], "counts": [11950, 2972],
                      "initial_parameter_hash": hash1["sha256"]}), flush=True)


def save_npz(np, path, **arrays):
    with path.open("xb") as handle:
        np.savez(handle, **arrays)
        handle.flush()
        os.fsync(handle.fileno())


def fit_predict(np, torch, health_receipt, approval):
    gate = root_gate(approval)
    if not (ART / "preflight-result.json").is_file():
        raise RuntimeError("Preflight must complete before fitting")
    if json.loads((ART / "preflight-result.json").read_text())["source_inputs"] != source_manifest():
        raise RuntimeError("Adapter changed after preflight; review required")
    claim_once("fit-predict")
    data = load_data(np)
    write_new_json(ART / "run-health.json", health_receipt)
    write_new_json(ART / "run-scalers.json", data["scalers"])
    expected_init = json.loads((ART / "preflight-initial-parameter-reference.json").read_text())["sha256"]
    predictions, checkpoints, init_hashes, training_progress = {}, {}, {}, []
    for variant in VARIANTS:
        xtrain, xtest = data["xtrain"].copy(), data["xtest"].copy()
        if variant.endswith("_price"):
            xtrain[:, :, 2] = 0
            xtest[:, :, 2] = 0
        start = time.monotonic()
        if variant.startswith("LSTM"):
            model = fresh_model(torch)
            initial = parameter_hash(model)["sha256"]
            if initial != expected_init:
                raise RuntimeError("Initial model hash differs from preflight")
            init_hashes[variant] = initial
            opts = dict(data["proposal"]["models"]["LSTM"]["optimizer"])
            opts.pop("name")
            opts["betas"] = tuple(opts["betas"])
            optimizer = torch.optim.Adam(model.parameters(), **opts)
            X = torch.from_numpy(xtrain.astype(np.float32))
            y = torch.from_numpy(data["ytrain"].astype(np.float32))
            model.train()
            for epoch in range(10):
                for offset in range(0, len(X), 64):
                    optimizer.zero_grad(set_to_none=True)
                    output = model(X[offset:offset + 64])
                    loss = torch.nn.functional.mse_loss(output, y[offset:offset + 64], reduction="mean")
                    if not torch.isfinite(loss).item():
                        raise RuntimeError("Nonfinite training loss")
                    loss.backward()
                    if any(t.grad is not None and not torch.isfinite(t.grad).all().item()
                           for t in model.parameters()):
                        raise RuntimeError("Nonfinite gradient")
                    optimizer.step()
                print(json.dumps({"variant": variant, "epoch_completed": epoch + 1}), flush=True)
            model.eval()
            pieces = []
            with torch.no_grad():
                test_tensor = torch.from_numpy(xtest.astype(np.float32))
                for offset in range(0, len(test_tensor), 64):
                    pieces.append(model(test_tensor[offset:offset + 64]).cpu().numpy().astype(np.float64))
            scaled_pred = np.concatenate(pieces)
            checkpoint = ART / (variant + ".final.pt")
            with checkpoint.open("xb") as handle:
                torch.save({"state_dict": model.state_dict(), "optimizer_state_dict": optimizer.state_dict(),
                            "initial_parameter_hash": initial, "final_epoch": 10,
                            "proposal_sha256": EXPECTED_PROPOSAL}, handle)
                handle.flush()
                os.fsync(handle.fileno())
            del optimizer, model, X, y, test_tensor
        else:
            X = xtrain.reshape(len(xtrain), 90)
            Z = xtest.reshape(len(xtest), 90)
            xbar = X.mean(axis=0, dtype=np.float64)
            ybar = float(data["ytrain"].mean(dtype=np.float64))
            centered_x = X - xbar
            centered_y = data["ytrain"] - ybar
            weights = np.linalg.solve(centered_x.T @ centered_x + np.eye(90, dtype=np.float64),
                                      centered_x.T @ centered_y)
            intercept = ybar - xbar @ weights
            scaled_pred = Z @ weights + intercept
            checkpoint = ART / (variant + ".final.npz")
            save_npz(np, checkpoint, weights=weights, intercept=np.asarray(intercept), alpha=np.asarray(1.0))
        pred = scaled_pred * data["scalers"]["target_population_std"] + data["scalers"]["target_mean"]
        if pred.shape != (2972,) or not np.isfinite(pred).all():
            raise RuntimeError("Nonfinite/mismatched full prediction vector")
        predictions[variant] = pred
        checkpoints[str(checkpoint)] = fingerprint(checkpoint)
        training_progress.append({"variant": variant, "completed_utc": utc(),
                                  "seconds": time.monotonic() - start})
    if init_hashes["LSTM_price"] != init_hashes["LSTM_state"]:
        raise RuntimeError("Paired initialization mismatch")
    # No test error or return calculations exist above this boundary.
    output_file = ART / "all-model-predictions.csv"
    with output_file.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["source_index", "system_time", "actual_mid", "last_known_mid"] + VARIANTS + ["unchanged_price"])
        for n, index in enumerate(data["indices"]["test"]):
            i = int(index)
            writer.writerow([i, data["timestamps"][i], repr(float(data["mid"][i])),
                             repr(float(data["mid"][i - 1]))] +
                            [repr(float(predictions[v][n])) for v in VARIANTS] +
                            [repr(float(data["mid"][i - 1]))])
        handle.flush()
        os.fsync(handle.fileno())
    settings = {"proposal": {"path": str(PROPOSAL), **fingerprint(PROPOSAL)},
                "source_inputs": source_manifest(), "approval": gate,
                "frozen_input_hashes": {str(x): fingerprint(x) for x in data["input_paths"].values()},
                "initial_parameter_hashes": init_hashes,
                "execution_order": VARIANTS, "progress": training_progress,
                "all_test_predictions_saved_before_scoring": True}
    write_new_json(ART / "run-settings.json", settings)
    sealed_files = {str(output_file): fingerprint(output_file),
                    str(ART / "run-scalers.json"): fingerprint(ART / "run-scalers.json"),
                    str(ART / "run-settings.json"): fingerprint(ART / "run-settings.json"), **checkpoints}
    write_new_json(ART / "predictions-sealed-before-scoring.json",
                   {"status": "ALL_FOUR_PREDICTIONS_AND_FINAL_CHECKPOINTS_SEALED_NO_TEST_SCORES_YET",
                    "at_utc": utc(), "rows": 2972, "files": sealed_files,
                    "not_prospective_market_seal": True})
    print(json.dumps({"status": "PREDICTIONS_SEALED_STOP_BEFORE_AGGREGATE_SCORING"}), flush=True)


def score(np, approval):
    gate = root_gate(approval)
    sealpath = ART / "predictions-sealed-before-scoring.json"
    seal = json.loads(sealpath.read_text())
    for path, expected in seal["files"].items():
        if fingerprint(path) != expected:
            raise RuntimeError("Sealed output changed before scoring")
    claim_once("scoring")
    with (ART / "all-model-predictions.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 2972:
        raise RuntimeError("Full prediction row count mismatch")
    actual = np.asarray([float(x["actual_mid"]) for x in rows], dtype=np.float64)
    previous = np.asarray([float(x["last_known_mid"]) for x in rows], dtype=np.float64)
    if not np.isfinite(actual).all() or not np.isfinite(previous).all() or not (previous > 0).all():
        raise RuntimeError("Invalid sealed truth/denominator")
    actual_return = (actual - previous) / previous
    dates = [datetime.fromisoformat(x["system_time"]).date().isoformat() for x in rows]
    results = {}
    for name in VARIANTS + ["unchanged_price"]:
        pred = np.asarray([float(x[name]) for x in rows], dtype=np.float64)
        if not np.isfinite(pred).all():
            raise RuntimeError("Invalid sealed prediction")
        predicted_return = (pred - previous) / previous
        error = predicted_return - actual_return
        daily = {}
        for day in sorted(set(dates)):
            mask = np.asarray([x == day for x in dates])
            daily[day] = {"count": int(mask.sum()), "MSE": float(np.mean(error[mask] ** 2)),
                          "MAE_basis_points": float(np.mean(np.abs(error[mask])) * 10000),
                          "signed_error_bias_basis_points": float(np.mean(error[mask]) * 10000)}
        results[name] = {"count": len(rows), "MSE": float(np.mean(error ** 2)),
                         "MAE_basis_points": float(np.mean(np.abs(error)) * 10000),
                         "signed_error_bias_basis_points": float(np.mean(error) * 10000),
                         "all_partial_UTC_dates": daily}
    primary = results["LSTM_state"]["MSE"]
    comparisons = {}
    passed = True
    for baseline in ["LSTM_price", "unchanged_price"]:
        mse = results[baseline]["MSE"]
        comparison_pass = mse > 0 and primary <= 0.99 * mse
        passed = passed and comparison_pass
        comparisons[baseline] = {"baseline_MSE": mse,
                                  "relative_MSE_reduction": None if mse <= 0 else 1 - primary / mse,
                                  "at_least_1percent": comparison_pass}
    write_new_json(ART / "evaluation-results.json",
                   {"status": "EARLY_CANDIDATE_ONLY" if passed else "NOT_SUPPORTED_THIS_SETUP",
                    "at_utc": utc(), "prior_prediction_seal": {"path": str(sealpath), **fingerprint(sealpath)},
                    "root_approval": gate, "results": results, "primary_comparisons": comparisons,
                    "daily_MSE_state_minus_baselines": {
                        day: {name: results["LSTM_state"]["all_partial_UTC_dates"][day]["MSE"] -
                                    results[name]["all_partial_UTC_dates"][day]["MSE"]
                              for name in ["LSTM_price", "unchanged_price"]}
                        for day in sorted(set(dates))},
                    "not_profit_or_stable_edge_or_capacity": True,
                    "overlapping_windows_three_partial_days_not_independent": True})
    print(json.dumps({"status": "SCORING_COMPLETED_ALL_VARIANTS_RETAINED"}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["preflight", "fit_predict", "score"])
    parser.add_argument("--approval", default=None)
    args = parser.parse_args()
    require_supervision()
    np, torch, health_receipt = health()
    if args.stage == "preflight":
        preflight(np, torch, health_receipt)
    elif args.stage == "fit_predict":
        fit_predict(np, torch, health_receipt, args.approval)
    else:
        score(np, args.approval)


if __name__ == "__main__":
    main()
