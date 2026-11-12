"""Own synthetic fixtures only; never accesses the customer market archive."""
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_qc", ROOT / "inspect_local_only.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
baseline_policy = dict(module.POLICY)
fixture_root = ROOT / "synthetic-check-fixed"
fixture_root.mkdir(exist_ok=False)
header = "exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount\n"
row = "bitstamp,BTCUSD,1640995800000000,1640995800000001,1,101,100,1\n"
results = []
for case in ("valid", "bad_crc", "missing_column", "line_limit"):
    directory = fixture_root / case
    directory.mkdir()
    module.LOCAL = directory
    module.ROOT = directory
    module.POLICY = dict(baseline_policy)
    if case == "missing_column":
        body = b"exchange,symbol\nbitstamp,BTCUSD\n"
    elif case == "line_limit":
        body = (header + row).encode()
        module.POLICY["maximum_line_bytes"] = 16
    else:
        body = (header + row).encode()
    packed = bytearray(gzip.compress(body))
    if case == "bad_crc":
        packed[-8] ^= 1
    (directory / baseline_policy["input_file"]).write_bytes(packed)
    (directory / baseline_policy["private_transport_receipt"]).write_text(
        json.dumps({"complete": True, "sha256": hashlib.sha256(packed).hexdigest()}))
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        exit_code = module.main()
    public = json.loads(captured.getvalue())
    private = json.loads((directory / baseline_policy["output_private_json"]).read_text())
    assert exit_code == 0
    assert public["job_status"] == "LOCAL_INSPECTION_ATTEMPT_FINISHED_PRIVATE_REPORTS_WRITTEN"
    assert private["inspection_completed"] == (case == "valid")
    assert set(public) == {"job_status", "private_result_not_encoded_in_public_status",
                           "market_rows_or_derived_outcomes_returned_to_AI", "private_report_json",
                           "private_report_html", "network_model_financial_or_trade_execution"}
    assert (directory / baseline_policy["output_private_html"]).read_text().startswith("<!doctype html>")
    results.append({"own_synthetic_case": case, "privacy_boundary_and_completion_check": "PASS"})
(fixture_root / "summary.json").write_text(json.dumps({"own_synthetic_only": True, "results": results}, indent=2) + "\n")
print(json.dumps({"own_synthetic_only": True, "cases": results, "real_market_archive_accessed": False}))
