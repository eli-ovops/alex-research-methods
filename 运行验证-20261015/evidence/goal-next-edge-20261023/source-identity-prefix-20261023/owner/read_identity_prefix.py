#!/usr/bin/env python3
"""One bounded gzip prefix read; retain header and first-row identity only."""
from pathlib import Path
import codecs
import csv
import datetime as dt
import hashlib
import io
import json
import os
import resource
import signal
import time
import zlib

BASE = Path(__file__).resolve().parent
SOURCE = Path("/Volumes/EXTERNAL/\u4e9a\u529b\u514b\u65af /\u8fd0\u884c\u9a8c\u8bc1-20261015/evidence/goal-next-edge-20261023/causal-pair-october-readonly-20261023/owner/kraken_BTC-USD_quotes_2026-10-01.csv.gz.part")
COMPRESSED_CAP = 65536
EXPANDED_CAP = 262144
CPU_CAP = 10

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def cpu_stop(signum, frame):
    raise RuntimeError("CPU_CAP")

def main():
    receipt_path = BASE / "receipt.json"
    assert not receipt_path.exists()
    started_cpu = time.process_time()
    started_wall = time.monotonic()
    result = {
        "started_utc": stamp(), "pid": os.getpid(),
        "input_absolute_path": str(SOURCE),
        "method_sha256": hashlib.sha256((BASE / "METHOD_BEFORE_READ.md").read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "compressed_input_cap": COMPRESSED_CAP, "expanded_output_cap": EXPANDED_CAP,
        "compressed_bytes_read": 0, "expanded_bytes_produced": 0,
        "source_hash_performed": False, "source_eof_or_crc_attempted": False,
        "source_open_count": 0, "network_requests": 0,
        "expected": {"exchange": "kraken", "symbol": "BTC-USD"},
        "whole_file_or_all_prior_rows_identity_proven": False,
        "actual_model_effort": "UNKNOWN"
    }
    exit_code = 2
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_CAP, CPU_CAP + 1))
        signal.signal(signal.SIGXCPU, cpu_stop)
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        expanded = bytearray()
        first_bytes = b""
        result["source_open_count"] = 1
        with SOURCE.open("rb") as source:
            while result["compressed_bytes_read"] < COMPRESSED_CAP:
                if time.process_time() - started_cpu > CPU_CAP:
                    raise RuntimeError("CPU_CAP")
                raw = source.read(min(8192, COMPRESSED_CAP - result["compressed_bytes_read"]))
                if not raw:
                    raise RuntimeError("PREFIX_SOURCE_ENDED_BEFORE_FIRST_RECORD")
                if not first_bytes:
                    first_bytes = raw[:10]
                    if len(first_bytes) < 10 or first_bytes[:3] != b"\x1f\x8b\x08":
                        raise RuntimeError("GZIP_FIXED_HEADER_MISMATCH")
                result["compressed_bytes_read"] += len(raw)
                remaining = EXPANDED_CAP - len(expanded)
                if remaining <= 0:
                    raise RuntimeError("EXPANDED_PREFIX_CAP")
                expanded.extend(decoder.decompress(raw, remaining))
                result["expanded_bytes_produced"] = len(expanded)
                if expanded.count(b"\n") >= 2:
                    break
                if len(expanded) >= EXPANDED_CAP:
                    raise RuntimeError("EXPANDED_PREFIX_CAP")
            else:
                raise RuntimeError("COMPRESSED_PREFIX_CAP")
        # Decode only the retained prefix. Never convert numeric market fields.
        text = codecs.getincrementaldecoder("utf-8-sig")().decode(bytes(expanded), final=False)
        rows = csv.reader(io.StringIO(text), strict=True)
        header = next(rows)
        first_row = next(rows)
        if len(header) != len(first_row):
            raise RuntimeError("FIRST_CSV_RECORD_WIDTH_MISMATCH")
        if header.count("exchange") != 1 or header.count("symbol") != 1:
            raise RuntimeError("IDENTITY_HEADER_NOT_UNIQUE")
        actual = {"exchange": first_row[header.index("exchange")],
                  "symbol": first_row[header.index("symbol")]}
        header_end = expanded.find(b"\n") + 1
        raw_header = bytes(expanded[:header_end]).decode("utf-8")
        result.update({
            "status": "PASS_BOUNDED_PREFIX_IDENTITY_EXTRACTED",
            "gzip_fixed_header_hex": first_bytes.hex(),
            "raw_csv_header_with_line_ending": raw_header,
            "csv_header_fields": header,
            "actual_first_data_row_identity": actual,
            "per_field_equal_expected": {
                k: actual[k] == result["expected"][k] for k in actual
            },
            "first_data_record_index_1_based": 1,
            "prefix_only": True,
            "partial_source_not_exhausted_or_validated": True,
            "gzip_eof_observed_incidentally": decoder.eof,
            "bounded_decoder_unconsumed_tail_bytes": len(decoder.unconsumed_tail),
            "other_market_fields_saved": False,
            "interpretation": "Only this first CSV record. Filename dataset ID and body symbol may differ; no all-row inference or old QC status rewrite."
        })
        exit_code = 0
    except BaseException as error:
        result["status"] = "STOP_BOUNDED_PREFIX_READ_ERROR"
        result["error_type"] = type(error).__name__
        # Only our fixed code, never arbitrary library messages with source data.
        result["error_code"] = str(error) if isinstance(error, RuntimeError) else "LIBRARY_ERROR_NO_MARKET_CONTENT_SAVED"
    finally:
        result["completed_utc"] = stamp()
        result["exit_code"] = exit_code
        result["cpu_seconds"] = time.process_time() - started_cpu
        result["wall_seconds"] = time.monotonic() - started_wall
        result["prices_quantities_labels_computed_or_exported"] = False
        with receipt_path.open("x", encoding="utf-8") as out:
            json.dump(result, out, ensure_ascii=True, indent=2)
            out.write("\n")
    print(json.dumps({"status": result["status"], "pid": result["pid"], "exit_code": exit_code,
                      "actual_first_data_row_identity": result.get("actual_first_data_row_identity"),
                      "compressed_bytes_read": result["compressed_bytes_read"],
                      "expanded_bytes_produced": result["expanded_bytes_produced"]}))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())

