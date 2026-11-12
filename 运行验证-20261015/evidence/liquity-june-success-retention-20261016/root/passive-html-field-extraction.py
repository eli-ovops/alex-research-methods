"""Passive research extraction from already saved original HTML; no network or page execution."""
from pathlib import Path
from html.parser import HTMLParser
from decimal import Decimal
from datetime import datetime, timezone
import sys
import json
import re
import hashlib


class Node:
    def __init__(self, tag, attrs, start, parent=None):
        self.tag, self.attrs, self.start, self.parent = tag, dict(attrs), start, parent
        self.end, self.children = None, []

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def all(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.all()


class Reader(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.lines = [0] + [m.end() for m in re.finditer('\n', html)]
        self.root = Node('root', [], 0)
        self.stack = [self.root]

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.position(), self.stack[-1])
        self.stack[-1].children.append(node)
        if tag in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            node.end = self.position() + len(self.get_starttag_text())
        else:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                for node in self.stack[index:]:
                    node.end = self.position() + len(tag) + 3
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def amount_wei(text):
    match = re.search(r'([\d.]+)\s*(ETH|wei)\b', text)
    assert match, ('missing amount/unit', text)
    value = Decimal(match.group(1)) * (10**18 if match.group(2) == 'ETH' else 1)
    assert value == int(value), text
    return int(value)


stage = Path(sys.argv[1]).resolve()
scope = json.loads((stage / 'root/fixed-scope-before-cost-read.json').read_text())
transactions = []
for item in scope['fixed_items']:
    if not item.get('full_tx_HTML'):
        continue
    path = Path(item['full_tx_HTML'])
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['HTML_sha256']
    html = raw.decode('utf-8')
    reader = Reader(html)
    reader.feed(html)
    nodes = list(reader.root.all())
    ids = {}
    for node in nodes:
        if 'id' in node.attrs:
            ids.setdefault(node.attrs['id'], []).append(node)

    def field(key):
        assert len(ids.get(key, [])) == 1, (item['tx'], key)
        node = ids[key][0]
        return {'id': key, 'text': re.sub(r'\s+', ' ', node.text()).strip(), 'char_start': node.start, 'char_end': node.end}

    fields = {key: field(key) for key in ('data-fadd', 'data-val', 'data-txfee', 'data-gas', 'ContentPlaceHolder1_spanGasUsedByTxn')}
    start = html.find('<!-- To -->')
    end = html.find('<!-- End To -->', start)
    assert start >= 0 and end > start
    addresses = re.findall(r'/address/(0x[a-fA-F0-9]{40})', html[start:end])
    assert addresses
    fee = amount_wei(fields['data-txfee']['text'])
    value = amount_wei(fields['data-val']['text'])
    gas_price = Decimal(re.search(r'([\d.]+)\s*Gwei', fields['data-gas']['text']).group(1)) * 10**9
    used = int(re.match(r'([\d,]+)', fields['ContentPlaceHolder1_spanGasUsedByTxn']['text']).group(1).replace(',', ''))
    assert gas_price == int(gas_price) and fee == used * gas_price
    flows = []
    for node in nodes:
        if not re.fullmatch(r'tb_internaltx_\d+', node.attrs.get('id', '')):
            continue
        row = node
        while row is not None and row.tag != 'tr':
            row = row.parent
        assert row is not None
        addresses_in_row, amounts = [], []
        for child in row.all():
            if child.tag == 'a' and re.fullmatch(r'/address/0x[0-9a-fA-F]{40}', child.attrs.get('href', '')):
                addresses_in_row.append(child.attrs['href'].split('/')[-1].lower())
            if child.tag == 'td' and re.search(r'[\d.]\s*(ETH|wei)\b', child.text()):
                amounts.append(amount_wei(child.text()))
        assert len(addresses_in_row) == 2 and len(amounts) == 1, (item['tx'], addresses_in_row, amounts)
        flows.append({'index_id': node.attrs['id'], 'from': addresses_in_row[0], 'to': addresses_in_row[1], 'wei': str(amounts[0]), 'ETH': str(Decimal(amounts[0]) / 10**18), 'text': re.sub(r'\s+', ' ', row.text()).strip(), 'char_start': row.start, 'char_end': row.end})
    transactions.append({'tx': item['tx'], 'block': item['block'], 'from': fields['data-fadd']['text'].lower(), 'to': addresses[0].lower(), 'top_value_wei': str(value), 'gas_wei': str(fee), 'gas_ETH': str(Decimal(fee) / 10**18), 'gas_used': used, 'effective_gas_price_wei': str(int(gas_price)), 'fields': fields, 'visible_native_flows': flows, 'source_path': str(path), 'source_sha256': item['HTML_sha256'], 'native_absence_is_not_zero': not bool(flows), 'fixed_WETH_raw': item['fixed_WETH_raw'], 'variable_WETH_raw': item['variable_collateral_raw']})
assert len(transactions) == 9
result = {'at_utc': datetime.now(timezone.utc).isoformat(), 'method': 'Passive saved HTML tags/text/attributes only, gas fee exact crosscheck; no page/scripts execution, network or new net result', 'transactions': transactions, 'model_EVM_backtest_trade_network_calls': 0}
(stage / 'root/existing9-gas-topvalue-native-field-extraction.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
for row in transactions:
    print(json.dumps({key: row[key] for key in ('tx', 'from', 'to', 'top_value_wei', 'gas_ETH', 'visible_native_flows')}, ensure_ascii=False))
