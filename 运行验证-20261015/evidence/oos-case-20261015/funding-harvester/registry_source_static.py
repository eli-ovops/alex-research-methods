"""
results/registry.parquet — append-only run index.

Each row records one full pipeline execution with provenance fields so any
run can be reproduced: git SHA, config hash, data hash, runtime, memory,
and top-level performance metrics.

Schema (all columns, nullable where source may be unavailable):
  run_id          str       uuid4 hex
  timestamp       str       ISO-8601 UTC
  git_sha         str       40-char hex (or "unknown")
  git_dirty       bool      True if working tree had uncommitted changes
  host            str       socket.gethostname()
  backend         str       "python" (future: "cpp")
  config_hash     str       MD5 of json-serialised FundingArbConfig
  data_hash       str       MD5 of DataFrame index+close column
  runtime_s       float     wall-clock seconds
  peak_memory_mb  float     RSS at peak (psutil)
  output_dir      str       path written to
  oos_sharpe      float     OOS net Sharpe ratio (or NaN)
  n_trades        int       total trades in OOS
  assets          str       comma-joined symbol list
  oos_start       str       OOS split date
"""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psutil

REGISTRY_PATH = Path("results") / "registry.parquet"


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def _peak_memory_mb() -> float:
    try:
        return psutil.Process().memory_info().rss / 1024 / 1024
    except Exception:
        return float("nan")


def _md5(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.md5(raw).hexdigest()


def config_hash(cfg_dict: dict) -> str:
    return _md5(cfg_dict)


def data_hash(df: pd.DataFrame) -> str:
    idx_bytes = df.index.astype(str).tolist()
    close_bytes = df["close"].tolist() if "close" in df.columns else []
    return _md5({"index": idx_bytes[:100], "close": close_bytes[:100], "len": len(df)})


# ---------------------------------------------------------------------------
# Registry write
# ---------------------------------------------------------------------------

def append_run(
    *,
    runtime_s: float,
    output_dir: str | Path,
    cfg_dict: dict | None = None,
    data_df: pd.DataFrame | None = None,
    oos_sharpe: float = float("nan"),
    n_trades: int = 0,
    assets: list[str] | None = None,
    oos_start: str = "",
    backend: str = "python",
) -> str:
    """
    Append one row to results/registry.parquet and return the run_id.

    Creates the parquet if it doesn't exist. Thread-unsafe — fine for single-
    process research runs. Do not call from concurrent workers.
    """
    run_id = uuid.uuid4().hex

    row = {
        "run_id":         run_id,
        "timestamp":      datetime.now(tz=timezone.utc).isoformat(),
        "git_sha":        _git_sha(),
        "git_dirty":      _git_dirty(),
        "host":           socket.gethostname(),
        "backend":        backend,
        "config_hash":    config_hash(cfg_dict) if cfg_dict else "",
        "data_hash":      data_hash(data_df) if data_df is not None else "",
        "runtime_s":      runtime_s,
        "peak_memory_mb": _peak_memory_mb(),
        "output_dir":     str(output_dir),
        "oos_sharpe":     oos_sharpe,
        "n_trades":       n_trades,
        "assets":         ",".join(assets or []),
        "oos_start":      oos_start,
    }

    new_df = pd.DataFrame([row])

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    if REGISTRY_PATH.exists():
        existing = pd.read_parquet(REGISTRY_PATH)
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_parquet(REGISTRY_PATH, index=False)
    return run_id
