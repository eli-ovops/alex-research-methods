"""Read SHA-bound owned checkpoints as tensor data only; never build/forward a model."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

start = time.monotonic()
HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2]
OLD = BASE / "evidence/BTC1min-fixed-evaluation-run-20261017/artifacts"
expected = {
    "LSTM_price.final.pt": "257cb2d4c7ede007f1aca9216b2394fffab6341b002c51064d9951f3ad10fef4",
    "LSTM_state.final.pt": "34690b7472e688dab73718475a2aa7e3bf0e354da01629908b0077e04988cd7e",
}
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"]:
    if os.environ.get(key) != "6":
        raise RuntimeError("Missing thread cap: " + key)
if not sys.dont_write_bytecode:
    raise RuntimeError("Bytecode writes enabled")
import torch
torch.set_num_threads(6)
torch.set_num_interop_threads(1)
records = {}
for name, sha in expected.items():
    path = OLD / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
        raise RuntimeError("Checkpoint SHA mismatch")
    saved = torch.load(path, weights_only=True, map_location="cpu")
    state = saved["state_dict"]
    if list(state["head.weight"].shape) != [1, 16] or list(state["head.bias"].shape) != [1]:
        raise RuntimeError("Unexpected owned head shape")
    if any(value.device.type != "cpu" for value in state.values()):
        raise RuntimeError("Non-CPU parameter")
    steps = []
    for state_value in saved["optimizer_state_dict"]["state"].values():
        step = state_value.get("step")
        steps.append(float(step.item()) if hasattr(step, "item") else step)
    records[name] = {
        "path": str(path), "sha256": sha, "bytes": path.stat().st_size,
        "method": "torch.load(weights_only=True,map_location='cpu') after stdlib zip/pickletools inspection",
        "head_weight": state["head.weight"].tolist()[0],
        "head_bias": state["head.bias"].tolist()[0],
        "state_parameter_shapes": {key: list(value.shape) for key, value in state.items()},
        "final_epoch_metadata": saved["final_epoch"],
        "optimizer_step_counters_only_not_loss_trajectory": steps,
        "initial_parameter_hash": saved["initial_parameter_hash"],
        "proposal_sha256": saved["proposal_sha256"],
    }
receipt = {
    "status": "PASS_OWNED_PARAMETER_DATA_READ_ONLY_NO_MODEL_CONSTRUCTION_OR_FORWARD",
    "at_utc": datetime.now(timezone.utc).isoformat(), "records": records,
    "torch_version": torch.__version__, "torch_threads": torch.get_num_threads(),
    "torch_interop_threads": torch.get_num_interop_threads(),
    "weights_only": True, "map_location": "cpu", "arbitrary_pickle_load": False,
    "imported_old_adapter": False, "model_construction_forward_training_prediction": 0,
    "bytecode_writes_disabled": sys.dont_write_bytecode,
    "elapsed_seconds": time.monotonic() - start,
    "process_peak_RSS_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
}
with (HERE / "owned-head-parameter-read.json").open("x") as handle:
    json.dump(receipt, handle, indent=2, allow_nan=False)
    handle.write("\n")
print(json.dumps({"status": receipt["status"], "elapsed_seconds": receipt["elapsed_seconds"]}))
