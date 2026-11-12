"""Passive HTML text extraction only; no JS, network, financial arithmetic."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent

class StaticText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.suppressed = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.suppressed += 1
        if not self.suppressed and tag in {"div", "p", "tr", "td", "li", "br", "h1", "h2", "h3", "span", "label"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.suppressed:
            self.suppressed -= 1
        if not self.suppressed and tag in {"div", "p", "tr", "td", "li", "h1", "h2", "h3", "span", "label"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)

source = ROOT / "action2-mantlescan.source.html"
raw = source.read_bytes()
parser = StaticText()
parser.feed(raw.decode("utf-8", errors="replace"))
lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(parser.parts).splitlines()]
text = "\n".join(line for line in lines if line) + "\n"
target = ROOT / "action2-mantlescan.static-text.txt"
target.write_text(text, encoding="utf-8")
metadata = {
    "source_file": source.name,
    "source_bytes": len(raw),
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "text_file": target.name,
    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    "source_js_or_source_code_executed": False,
    "network_requests": 0,
    "financial_arithmetic": False,
    "html_parser_only": True
}
(ROOT / "static-extraction-receipt.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metadata))
