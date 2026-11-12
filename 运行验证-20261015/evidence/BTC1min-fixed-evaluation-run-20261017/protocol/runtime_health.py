"""Owned adapter health check, not author source. No fitting or predictions."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone

PHASE = Path(__file__).resolve().parents[1]
BASE = PHASE.parents[1]
ART = PHASE / "artifacts"
EXPECTED_PROPOSAL = "969ac08ec3504d5960b0b7787ee3204a7b6b9eb656484de22ebd4e4fb105d983"
PROPOSAL = BASE / "evidence/BTC1min-fixed-evaluation-readiness-20261017/root/fixed-once-evaluation-proposal.json"
THREAD_ENV = {
    "OMP_NUM_THREADS": "6", "OMP_THREAD_LIMIT": "6",
    "OPENBLAS_NUM_THREADS": "6", "MKL_NUM_THREADS": "6",
    "VECLIB_MAXIMUM_THREADS": "6", "NUMEXPR_NUM_THREADS": "6",
    "BLIS_NUM_THREADS": "6", "PYTHONDONTWRITEBYTECODE": "1",
}


def fingerprint(path):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "bytes": path.stat().st_size}


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_new_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=True, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def health():
    for name, value in THREAD_ENV.items():
        if os.environ.get(name) != value:
            raise RuntimeError("Thread/no-bytecode environment mismatch: " + name)
    if fingerprint(PROPOSAL)["sha256"] != EXPECTED_PROPOSAL:
        raise RuntimeError("Frozen proposal changed")
    auth = json.loads((PHASE / "root/execution-authorization.json").read_text())
    if auth["proposal_sha256"] != EXPECTED_PROPOSAL or auth["approved_reply"] != "允许。":
        raise RuntimeError("Authorization identity mismatch")
    if datetime.now(timezone.utc) >= datetime.fromisoformat(auth["work_deadline_utc"]):
        raise RuntimeError("Authorized work deadline exceeded")
    if sys.version_info[:3] != (3, 12, 14):
        raise RuntimeError("Unexpected interpreter version: " + sys.version)
    # These are the first authorised scientific/model-package imports.
    import numpy as np
    import torch
    if np.__version__ != "2.2.6" or torch.__version__ != "2.8.0":
        raise RuntimeError("Unexpected NumPy/Torch version")
    torch.set_num_threads(6)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float32)
    if torch.get_num_threads() != 6 or torch.get_num_interop_threads() != 1:
        raise RuntimeError("Torch thread limits did not take effect")
    if not torch.are_deterministic_algorithms_enabled():
        raise RuntimeError("Deterministic algorithms request did not take effect")
    # Elementary numerical smoke checks, not a model forward or prediction.
    if float(np.array([1.0, 2.0], dtype=np.float64).sum()) != 3.0:
        raise RuntimeError("NumPy elementary smoke check failed")
    smoke = torch.tensor([1.0, 2.0], dtype=torch.float32, device="cpu")
    if smoke.device.type != "cpu" or float(smoke.sum().item()) != 3.0:
        raise RuntimeError("Torch CPU elementary smoke check failed")
    receipt = {
        "status": "PASS_ACTUAL_IMPORT_CPU_HEALTH_NO_MODEL_FIT_OR_FORWARD",
        "at_utc": utc(), "python": sys.version,
        "executable": sys.executable, "numpy": np.__version__,
        "torch": torch.__version__, "platform": platform.platform(),
        "torch_intraop_threads": torch.get_num_threads(),
        "torch_interop_threads": torch.get_num_interop_threads(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "default_dtype": str(torch.get_default_dtype()),
        "thread_environment": {k: os.environ.get(k) for k in THREAD_ENV},
        "smoke_device": str(smoke.device), "MPS_CUDA_compile_used": False,
        "initialization_or_training_or_inference": False,
        "bytecode_writes_disabled": sys.dont_write_bytecode,
        "proposal": {"path": str(PROPOSAL), **fingerprint(PROPOSAL)},
        "authorization": {"path": str(PHASE / "root/execution-authorization.json"),
                          **fingerprint(PHASE / "root/execution-authorization.json")},
    }
    if not sys.dont_write_bytecode:
        raise RuntimeError("Bytecode writes not disabled")
    return np, torch, receipt


if __name__ == "__main__":
    _, _, result = health()
    write_new_json(ART / "health-result.json", result)
    print(json.dumps({"status": result["status"], "versions": [result["numpy"], result["torch"]]}))
