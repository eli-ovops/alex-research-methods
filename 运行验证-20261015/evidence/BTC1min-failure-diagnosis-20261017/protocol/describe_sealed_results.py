"""Stdlib descriptive audit of sealed outputs, not a model or replacement score run."""
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import time
import zipfile

START = time.monotonic()
HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2]
RUN = BASE / "evidence/BTC1min-fixed-evaluation-run-20261017"
ART = RUN / "artifacts"
SCALERS = json.loads((ART / "run-scalers.json").read_text())
SEALED = json.loads((ART / "predictions-sealed-before-scoring.json").read_text())
PROPOSAL_PATH = BASE / "evidence/BTC1min-fixed-evaluation-readiness-20261017/root/fixed-once-evaluation-proposal.json"
PROPOSAL = json.loads(PROPOSAL_PATH.read_text())


def fp(path):
    raw = path.read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


for name, expected in SEALED["files"].items():
    if fp(Path(name)) != expected:
        raise RuntimeError("Sealed original changed")
rawcsv = Path(PROPOSAL["data"]["path"])
if fp(rawcsv)["sha256"] != PROPOSAL["data"]["sha256"]:
    raise RuntimeError("Source CSV identity mismatch")
with (ART / "all-model-predictions.csv").open(newline="") as handle:
    rows = list(csv.DictReader(handle))
if len(rows) != 2972:
    raise RuntimeError("Scope changed")
for row in rows:
    for key in ["actual_mid", "last_known_mid", "LSTM_price", "LSTM_state",
                "Ridge_price", "Ridge_state", "unchanged_price"]:
        row[key] = float(row[key])
    row["source_index"] = int(row["source_index"])
    row["date"] = datetime.fromisoformat(row["system_time"]).date().isoformat()
days = sorted({x["date"] for x in rows})
actual_source = []
timestamps = []
max_abs_scaled = 0.0
with rawcsv.open(newline="") as handle:
    for row in csv.DictReader(handle):
        m, s, bid, ask = [float(row[x]) for x in
                          ["midpoint", "spread", "bids_notional_0", "asks_notional_0"]]
        actual_source.append(m)
        timestamps.append(row["system_time"])
        for value, mean, sd in zip([m, s, (bid - ask) / (bid + ask)],
                                   SCALERS["input_mean"], SCALERS["input_population_std"]):
            max_abs_scaled = max(max_abs_scaled, abs((value - mean) / sd) if sd else 0)
if any(row["actual_mid"] != actual_source[row["source_index"]] or
       row["last_known_mid"] != actual_source[row["source_index"] - 1] or
       row["system_time"] != timestamps[row["source_index"]] for row in rows):
    raise RuntimeError("Existing output/source alignment changed")


def range_info(values):
    return {"count": len(values), "minimum": min(values), "maximum": max(values)}


train_target = [actual_source[i] for i in SCALERS["target_fit_indices"]]
train_input = [actual_source[i] for i in SCALERS["input_fit_rows"]]
train_min, train_max = min(train_target), max(train_target)


def observed_stats(model, subset):
    # Existing sealed errors only. No inferred or new model output is produced.
    errors = [(x[model] - x["actual_mid"]) / x["last_known_mid"] for x in subset]
    square_sum = math.fsum(x * x for x in errors)
    mse = square_sum / len(errors)
    mean = math.fsum(errors) / len(errors)
    variance = math.fsum((x - mean) ** 2 for x in errors) / len(errors)
    return {"count": len(errors), "SSE": square_sum, "MSE": mse,
            "RMSE_basis_points": math.sqrt(mse) * 10000,
            "MAE_basis_points": math.fsum(abs(x) for x in errors) / len(errors) * 10000,
            "signed_mean_error_basis_points": mean * 10000,
            "mean_error_squared": mean * mean,
            "mean_error_squared_over_MSE_bias_share": mean * mean / mse if mse else None,
            "population_error_variance": variance,
            "MSE_minus_variance_minus_mean_squared": mse - variance - mean * mean,
            "prediction_above_actual_count": sum(x > 0 for x in errors),
            "prediction_below_actual_count": sum(x < 0 for x in errors),
            "equal_count": sum(x == 0 for x in errors)}


models = ["LSTM_price", "LSTM_state", "Ridge_price", "Ridge_state", "unchanged_price"]
stats = {}
for model in models:
    overall = observed_stats(model, rows)
    daily = {day: observed_stats(model, [x for x in rows if x["date"] == day]) for day in days}
    for value in daily.values():
        value["share_of_this_model_total_squared_error"] = value["SSE"] / overall["SSE"]
    worst = sorted(rows, key=lambda x: abs((x[model] - x["actual_mid"]) / x["last_known_mid"]),
                   reverse=True)[:5]
    stats[model] = {"overall": overall, "all_partial_dates": daily,
                    "worst_five_existing_errors_not_exclusions": [
                        {"source_index": x["source_index"], "system_time": x["system_time"],
                         "actual_mid": x["actual_mid"], "last_known_mid": x["last_known_mid"],
                         "sealed_prediction": x[model],
                         "signed_error_basis_points": (x[model] - x["actual_mid"]) / x["last_known_mid"] * 10000}
                        for x in worst]}
baseline = stats["unchanged_price"]["overall"]
ratios = {model: {"MSE_ratio_to_persistence": stats[model]["overall"]["MSE"] / baseline["MSE"],
                  "RMSE_ratio_to_persistence": stats[model]["overall"]["RMSE_basis_points"] / baseline["RMSE_basis_points"],
                  "MAE_ratio_to_persistence": stats[model]["overall"]["MAE_basis_points"] / baseline["MAE_basis_points"]}
          for model in models}


def scope_ranges(subset):
    truths = [x["actual_mid"] for x in subset]
    result = {"actual_target": range_info(truths),
              "last_known_mid": range_info([x["last_known_mid"] for x in subset]),
              "sealed_predictions": {model: range_info([x[model] for x in subset]) for model in models},
              "actual_below_train_target_min_count": sum(x < train_min for x in truths),
              "actual_above_train_target_max_count": sum(x > train_max for x in truths),
              "outside_train_target_range_fraction": sum(x < train_min or x > train_max for x in truths) / len(truths),
              "outside_train_input_price_range_fraction": sum(x < min(train_input) or x > max(train_input) for x in truths) / len(truths)}
    return result


range_output = {"TRAIN_target_midpoint": range_info(train_target),
                "unique_TRAIN_input_midpoint": range_info(train_input),
                "TEST_all": scope_ranges(rows),
                "TEST_all_partial_dates": {day: scope_ranges([x for x in rows if x["date"] == day]) for day in days}}

# The theoretical range is algebra on parameter data, not another prediction.
heads = json.loads((HERE / "owned-head-parameter-read.json").read_text())
bounds = {}
for filename, parameter in heads["records"].items():
    model = filename.removesuffix(".final.pt")
    weight_sum = math.fsum(abs(x) for x in parameter["head_weight"])
    bias = parameter["head_bias"]
    low_z, high_z = bias - weight_sum, bias + weight_sum
    mean, sd = SCALERS["target_mean"], SCALERS["target_population_std"]
    low, high = mean + sd * low_z, mean + sd * high_z
    # Standard float32 dot/bias accumulation error guard, not fitted tolerance.
    unit = 2 ** -24
    gamma = 17 * unit / (1 - 17 * unit)
    guard = sd * gamma * (abs(bias) + weight_sum)
    below = [x for x in rows if x["actual_mid"] < low - guard]
    above = [x for x in rows if x["actual_mid"] > high + guard]
    def bound_counts(subset):
        return {"count": len(subset),
                "actual_below_conservative_lower_bound": sum(x["actual_mid"] < low - guard for x in subset),
                "actual_above_conservative_upper_bound": sum(x["actual_mid"] > high + guard for x in subset),
                "sealed_predictions_below_bound_minus_guard": sum(x[model] < low - guard for x in subset),
                "sealed_predictions_above_bound_plus_guard": sum(x[model] > high + guard for x in subset)}
    out_of_bound = below + above
    sse_out = math.fsum(((x[model] - x["actual_mid"]) / x["last_known_mid"]) ** 2 for x in out_of_bound)
    bounds[model] = {"head_bias": bias, "head_weight_L1": weight_sum,
                     "ideal_standardized_output_interval": [low_z, high_z],
                     "ideal_price_output_interval": [low, high],
                     "float32_dot_rounding_guard_price_units": guard,
                     "guard_formula": "gamma17*(abs(bias)+L1(weights))*target_std, gamma17=17u/(1-17u),u=2^-24",
                     "basis": "single unprojected LSTM output h_j=o_j*tanh(c_j), each component in[-1,1]; final Linear only",
                     "all_TEST": bound_counts(rows),
                     "all_partial_dates": {day: bound_counts([x for x in rows if x["date"] == day]) for day in days},
                     "fraction_of_existing_model_SSE_from_targets_outside_conservative_head_range": sse_out / stats[model]["overall"]["SSE"],
                     "not_hidden_activation_measurement": True,
                     "not_counterfactual_clipped_predictions_or_new_score": True}


def npy_read(raw):
    if raw[:6] != b"\x93NUMPY":
        raise RuntimeError("Not an NPY parameter member")
    version = tuple(raw[6:8])
    if version == (1, 0):
        length = struct.unpack("<H", raw[8:10])[0]
        offset = 10
    elif version in [(2, 0), (3, 0)]:
        length = struct.unpack("<I", raw[8:12])[0]
        offset = 12
    else:
        raise RuntimeError("Unknown NPY format")
    header = ast.literal_eval(raw[offset:offset + length].decode("latin1"))
    if header["descr"] != "<f8" or header["fortran_order"]:
        raise RuntimeError("Unexpected owned coefficient encoding")
    size = math.prod(header["shape"])
    payload = raw[offset + length:]
    if len(payload) != size * 8:
        raise RuntimeError("NPY parameter payload length mismatch")
    return header, list(struct.unpack("<" + "d" * size, payload))


ridge = {}
for model in ["Ridge_price", "Ridge_state"]:
    path = ART / (model + ".final.npz")
    with zipfile.ZipFile(path) as archive:
        arrays = {name: npy_read(archive.read(name)) for name in archive.namelist()}
    values = {name: data[1] for name, data in arrays.items()}
    weights = values["weights.npy"]
    ridge[model] = {"path": str(path), **fp(path),
                    "method": "stdlib zipfile/ast.literal_eval NPY header/struct float64 only; no np.load, matmul, solve or model prediction",
                    "coefficient_count": len(weights),
                    "all_coefficient_intercept_alpha_values_finite": all(math.isfinite(x) for v in values.values() for x in v),
                    "maximum_absolute_weight": max(abs(x) for x in weights),
                    "L1_weight": math.fsum(abs(x) for x in weights),
                    "intercept": values["intercept.npy"][0], "alpha": values["alpha.npy"][0]}

train_y_z_max = max(abs((x - SCALERS["target_mean"]) / SCALERS["target_population_std"]) for x in train_target)
n = 11950
numeric_bound = {"all_source_standardized_input_abs_upper": max_abs_scaled,
                 "TRAIN_standardized_target_abs_upper": train_y_z_max,
                 "centered_Gram_entry_abs_conservative_mathematical_upper": n * (2 * max_abs_scaled) ** 2,
                 "centered_RHS_entry_abs_conservative_mathematical_upper": n * (2 * max_abs_scaled) * (2 * train_y_z_max),
                 "double_max": float.fromhex('0x1.fffffffffffffp+1023'),
                 "scope": "Scalar mathematical input bounds only. No actual Gram/RHS matrix was rebuilt or evaluated; does not validate backend intermediates or explain warnings."}
stderr = (ART / "resource-session-0003-fit_predict.stderr.txt").read_text()
warning_lines = [x for x in stderr.splitlines() if "RuntimeWarning:" in x]
out = {"status": "DESCRIPTIVE_EXISTING_OUTPUT_DIAGNOSIS_NOT_A_NEW_MODEL_EXPERIMENT",
       "at_utc": datetime.now(timezone.utc).isoformat(),
       "ratios": ratios, "all_model_error_decomposition": stats,
       "training_and_test_price_ranges": range_output,
       "saved_parameter_head_bounds": bounds,
       "Ridge_saved_parameter_data_inspection": ridge,
       "Ridge_scalar_numeric_bounds_only": numeric_bound,
       "original_Ridge_warnings": {"count": len(warning_lines), "messages": warning_lines,
                                     "exact_variant_not_logged": True,
                                     "root_cause": "UNKNOWN; finite final values do not validate missing intermediate matrices",
                                     "Ridge_numeric_interpretation": "DEGRADED_PENDING_NUMERICAL_CHECK_NOT_PERFORMED_HERE",
                                     "not_a_cause_proven_for_LSTM": True},
       "all_2972_rows_retained": True, "no_date_or_extreme_row_removed": True,
       "new_model_output_forward_fit_or_prediction": 0,
       "elapsed_seconds": time.monotonic() - START}
with (HERE / "descriptive-output-decomposition.json").open("x") as handle:
    json.dump(out, handle, indent=2, allow_nan=False)
    handle.write("\n")
print(json.dumps({"ratios": ratios, "head_bounds": bounds,
                  "training_ranges": {k:v for k,v in range_output.items() if k.startswith('TRAIN') or k.startswith('unique')},
                  "test_range": range_output['TEST_all'],
                  "elapsed_seconds": out['elapsed_seconds']}, indent=2))
