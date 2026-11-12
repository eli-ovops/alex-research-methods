"""Read-only data QC. All observations remain on the customer's machine."""
import csv
import datetime as dt
import gzip
import hashlib
import html
import json
import math
import os
from pathlib import Path
import signal

ROOT = Path(__file__).resolve().parent
POLICY = json.loads((ROOT / "policy.json").read_text())
LOCAL = Path(POLICY["input_directory"])
EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def epoch_us(value):
    delta = dt.datetime.fromisoformat(value) - EPOCH
    return (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds


def show_us(value):
    return "未取得" if value is None else (EPOCH + dt.timedelta(microseconds=value)).isoformat()


def deadline(_signum, _frame):
    raise TimeoutError("fixed QC deadline")


def require_columns(columns):
    if not columns or not set(POLICY["required_columns"]).issubset(columns):
        raise ValueError("标准字段缺失")
    if POLICY["reject_duplicate_header_names"] and len(columns) != len(set(columns)):
        raise ValueError("表头列名重复，停止而不覆盖字段")


class BoundedLines:
    def __init__(self, stream):
        self.stream = stream
        self.expanded = 0
        self.first = True

    def __iter__(self):
        return self

    def __next__(self):
        raw = self.stream.readline(POLICY["maximum_line_bytes"] + 1)
        if not raw:
            raise StopIteration
        self.expanded += len(raw)
        if len(raw) > POLICY["maximum_line_bytes"]:
            raise ValueError("fixed line-size limit")
        if self.expanded > POLICY["maximum_expanded_bytes"]:
            raise ValueError("fixed expansion limit")
        encoding = "utf-8-sig" if self.first else "utf-8"
        self.first = False
        return raw.decode(encoding)


def inspect():
    result = {"start_UTC": utc(), "inspection_completed": False, "gzip_full_read_CRC": False}
    source = LOCAL / POLICY["input_file"]
    receipt = json.loads((LOCAL / POLICY["private_transport_receipt"]).read_text())
    if not receipt.get("complete") or source.stat().st_size > POLICY["maximum_compressed_bytes"]:
        raise ValueError("source identity or size precondition")
    digest = hashlib.sha256()
    compressed_seen = 0
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(262144), b""):
            compressed_seen += len(chunk)
            if compressed_seen > POLICY["maximum_compressed_bytes"]:
                raise ValueError("fixed compressed-size limit")
            digest.update(chunk)
    result["source_sha256"] = digest.hexdigest()
    result["matches_local_transfer_receipt"] = digest.hexdigest() == receipt.get("sha256")
    if not result["matches_local_transfer_receipt"]:
        raise ValueError("local source changed")
    start, end = [epoch_us(x) for x in POLICY["observation_window_UTC"]]
    day_start = epoch_us(POLICY["expected_local_date_UTC"] + "T00:00:00+00:00")
    anchors = {str(epoch_us(x)): {"anchor_UTC": x, "latest_at_or_before_local_us": None,
                                 "earliest_after_local_us": None} for x in POLICY["clock_anchors_UTC"]}
    numeric = ("ask_price", "ask_amount", "bid_price", "bid_amount")
    counts = {k: 0 for k in ("rows", "bad_shape", "wrong_identity", "invalid_timestamp", "local_outside_day",
                             "local_clock_backsteps", "exchange_clock_backsteps", "equal_local_timestamp",
                             "adjacent_identical_rows", "exchange_later_than_local", "crossed_quote_rows",
                             "window_rows_by_local", "window_rows_by_exchange")}
    missing, invalid = {k: 0 for k in numeric}, {k: 0 for k in numeric}
    first_local = last_local = previous_local = previous_exchange = None
    previous_row = None
    max_gap = 0
    with gzip.open(source, "rb") as stream:
        lines = BoundedLines(stream)
        csv.field_size_limit(4096)
        rows = csv.DictReader(lines)
        result["columns"] = rows.fieldnames
        result["required_columns_present"] = bool(rows.fieldnames) and set(POLICY["required_columns"]).issubset(rows.fieldnames)
        require_columns(rows.fieldnames)
        result["header_unique"] = len(rows.fieldnames) == len(set(rows.fieldnames))
        for row in rows:
            if counts["rows"] >= POLICY["maximum_rows"]:
                raise ValueError("fixed row-count limit")
            counts["rows"] += 1
            if None in row or any(row.get(k) is None for k in POLICY["required_columns"]):
                counts["bad_shape"] += 1
                continue
            canonical = tuple(row.get(k) for k in POLICY["required_columns"])
            counts["adjacent_identical_rows"] += canonical == previous_row
            previous_row = canonical
            if row["exchange"] != POLICY["allowed_exchange"] or row["symbol"] not in POLICY["allowed_symbol_aliases"]:
                counts["wrong_identity"] += 1
            values = {}
            for name in numeric:
                if row[name] == "":
                    missing[name] += 1
                    continue
                try:
                    value = float(row[name])
                    if not math.isfinite(value) or value < 0 or (name.endswith("price") and value == 0):
                        raise ValueError("invalid quote value")
                    values[name] = value
                except ValueError:
                    invalid[name] += 1
            if "bid_price" in values and "ask_price" in values:
                counts["crossed_quote_rows"] += values["bid_price"] > values["ask_price"]
            try:
                local, exchange = int(row["local_timestamp"]), int(row["timestamp"])
                if local <= 0 or exchange <= 0:
                    raise ValueError("invalid clock")
            except ValueError:
                counts["invalid_timestamp"] += 1
                continue
            first_local = local if first_local is None else min(first_local, local)
            last_local = local if last_local is None else max(last_local, local)
            counts["local_outside_day"] += not (day_start <= local < day_start + 86400000000)
            if previous_local is not None:
                counts["local_clock_backsteps"] += local < previous_local
                counts["equal_local_timestamp"] += local == previous_local
                max_gap = max(max_gap, local - previous_local)
            if previous_exchange is not None:
                counts["exchange_clock_backsteps"] += exchange < previous_exchange
            previous_local, previous_exchange = local, exchange
            counts["exchange_later_than_local"] += exchange > local
            counts["window_rows_by_local"] += start <= local < end
            counts["window_rows_by_exchange"] += start <= exchange < end
            for target, anchor in anchors.items():
                target = int(target)
                if local <= target:
                    old = anchor["latest_at_or_before_local_us"]
                    anchor["latest_at_or_before_local_us"] = local if old is None else max(old, local)
                else:
                    old = anchor["earliest_after_local_us"]
                    anchor["earliest_after_local_us"] = local if old is None else min(old, local)
        result["expanded_bytes"] = lines.expanded
    result.update({"inspection_completed": True, "gzip_full_read_CRC": True, "counts": counts,
                   "missing_numeric": missing, "invalid_numeric": invalid,
                   "first_local_UTC": show_us(first_local), "last_local_UTC": show_us(last_local),
                   "maximum_adjacent_local_gap_us": max_gap, "anchors": anchors})
    result["structural_findings_require_review"] = (
        counts["rows"] == 0 or any(counts[k] for k in ("bad_shape", "wrong_identity", "invalid_timestamp", "local_outside_day", "local_clock_backsteps"))
        or any(invalid.values()))
    return result


def render(result):
    completed = result.get("inspection_completed", False)
    if not completed:
        conclusion = "本次检查未完整完成；保持未判定，不修复或重跑。"
    elif result["structural_findings_require_review"]:
        conclusion = "已完成检查，存在需核查的结构或字段问题；不能认证目标数据可用。"
    else:
        conclusion = "容器与所列结构检查未触发问题；连续性、单位、输入可用性及成交仍待核。"
    entries = [("文件与本机下载收据一致", result.get("matches_local_transfer_receipt", "未完成")),
               ("gzip读至文件尾并校验CRC", result.get("gzip_full_read_CRC", False)),
               ("标准字段齐全", result.get("required_columns_present", "未完成")),
               ("表头列名无重复", result.get("header_unique", "未完成")),
               ("完整检查结束", completed)]
    labels = {
        "rows": "数据行数", "bad_shape": "列数/字段形状异常行", "wrong_identity": "交易所或币对标识不匹配行",
        "invalid_timestamp": "时间戳格式异常行", "local_outside_day": "本地到达时间不在目标日的行",
        "local_clock_backsteps": "本地到达时钟回退次数", "exchange_clock_backsteps": "交易所时钟回退次数",
        "equal_local_timestamp": "相邻本地时间戳相同次数", "adjacent_identical_rows": "相邻字段完全相同次数",
        "exchange_later_than_local": "交易所时间晚于本地时间的行", "crossed_quote_rows": "买价高于卖价的行",
        "window_rows_by_local": "本地时钟落入固定窗口的行", "window_rows_by_exchange": "交易所时钟落入固定窗口的行"
    }
    for k, v in result.get("counts", {}).items():
        entries.append((labels[k], v))
    entries.extend([
        ("第一条本地到达时间（UTC）", result.get("first_local_UTC", "未完成")),
        ("最后一条本地到达时间（UTC）", result.get("last_local_UTC", "未完成")),
        ("各数值字段缺值次数", result.get("missing_numeric", "未完成")),
        ("各数值字段非法值次数", result.get("invalid_numeric", "未完成"))
    ])
    table = "".join("<tr><td>" + html.escape(str(k)) + "</td><td>" + html.escape(str(v)) + "</td></tr>" for k, v in entries)
    return ("<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>本机报价文件核查</title>"
            "<style>body{max-width:900px;margin:40px auto;padding:0 24px;font:17px/1.7 system-ui;color:#182c35;background:#f7f8f4}"
            "h1{font-size:30px}table{border-collapse:collapse;width:100%;background:white}td{padding:8px 14px;border-bottom:1px solid #ddd}"
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;padding:20px}strong{color:#7c3922}</style>"
            "<h1>2022元旦报价文件：本机数据核查</h1><p><strong>仅供本机个人研究。含数据及衍生结果，请勿上传外部AI服务。</strong></p>"
            "<p>字段说明：bid_price是最高买价，ask_price是最低卖价；bid_amount/ask_amount是对应挂单数量，具体单位仍待来源绑定。"
            "timestamp是交易所时钟，local_timestamp是采集端到达时钟；它们不等于你的程序当时收到数据的时间。</p>"
            "<p>" + html.escape(conclusion) + "</p><table>" + table + "</table>"
            "<p>检查窗口：UTC [00:08,00:15)，两个时钟分别统计；本地日界约束仅用于local_timestamp。锚点00:10及00:12仅供时钟覆盖定位，不是已证输入可用或下单时点。</p>"
            "<p>报价是事件流，更新间隔不等于断线；CSV不含断线事件。相同时间戳、相邻重复或交易所时钟回退需按来源解释。"
            "只查相邻完全重复，未查全部非相邻重复。空侧另计，未修复或丢弃原文件。</p>"
            "<p>没有比较卖单数量与可用挂单量，没有计算价差成本、费用、冲击、收益或资金容量。"
            "本时段来自已研究历史，不是新独立样本。技术检查通过不代表未来净盈利。</p>"
            "<h2>完整本机检查原件</h2><pre>" + html.escape(json.dumps(result, ensure_ascii=False, indent=2)) + "</pre></html>")


def main():
    os.umask(0o077)
    with (LOCAL / POLICY["single_attempt_lock"]).open("x") as lock:
        lock.write("One local data-inspection attempt; never automatically rerun.\n")
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, POLICY["maximum_seconds"])
    try:
        result = inspect()
    except Exception as error:
        result = {"inspection_completed": False, "error_class": type(error).__name__, "error_detail": str(error)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    result["end_UTC"] = utc()
    with (LOCAL / POLICY["output_private_json"]).open("x") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
    with (LOCAL / POLICY["output_private_html"]).open("x") as output:
        output.write(render(result))
    public = {"job_status": "LOCAL_INSPECTION_ATTEMPT_FINISHED_PRIVATE_REPORTS_WRITTEN",
              "private_result_not_encoded_in_public_status": True,
              "market_rows_or_derived_outcomes_returned_to_AI": False,
              "private_report_json": str(LOCAL / POLICY["output_private_json"]),
              "private_report_html": str(LOCAL / POLICY["output_private_html"]),
              "network_model_financial_or_trade_execution": False}
    with (ROOT / "job-public.json").open("x") as output:
        json.dump(public, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps(public, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
