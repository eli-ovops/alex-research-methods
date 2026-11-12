"""Account already occurred original flows, not a strategy, simulation or backtest."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timezone
import json
import hashlib
import sys

stage = Path(sys.argv[1]).resolve()
base = stage.parents[1]
root = stage / 'root'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
WITHDRAW = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'
DEPOSIT = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'
scope = json.loads((root / 'fixed-scope-before-cost-read.json').read_text())
nine = json.loads((root / 'existing9-gas-topvalue-native-field-extraction.json').read_text())['transactions']
boundary = json.loads((stage / 'protocol/accounting-boundary-review.json').read_text())
facts = {x['tx']: x for x in boundary['nine_transaction_facts']}
prior_path = base / 'evidence/liquity-reproducibility-20261016/race-audit/derived.json'
prior = {x['hash']: x for x in json.loads(prior_path.read_text())['nine_successes']}
old_events_path = base / 'evidence/complete-ledger-case-20261016/liquity-raw-event-data/root/june-decoded-and-asset-sums.json'
old_events = json.loads(old_events_path.read_text())
event_map = {x['transaction_hash']: x for x in old_events['events']}
classification = json.loads((root / 'accounting-classification-before-net-calculation.json').read_text())
class_map = {x['tx']: x for x in classification['rows']}


def serialize(vector):
    return {key: str(value) for key, value in sorted(vector.items()) if value != 0}


def compute_vectors(sender, top_to, top_value, gas, transfers, withdrawals, deposits, native):
    vector = defaultdict(lambda: defaultdict(int))
    def transfer(asset, source, target, amount):
        vector[source][asset] -= amount
        vector[target][asset] += amount
    transfer('ETH_wei', sender, top_to, top_value)
    vector[sender]['ETH_wei'] -= gas
    for flow in native:
        transfer('ETH_wei', flow['from'], flow['to'], int(flow['wei']))
    for flow in transfers:
        transfer(flow['token'] + '_raw', flow['from'], flow['to'], int(flow['raw']))
    for flow in withdrawals:
        vector[flow['address']][WETH + '_raw'] -= int(flow['raw'])
    for flow in deposits:
        vector[flow['address']][WETH + '_raw'] += int(flow['raw'])
    return vector


def selected_sum(vectors, addresses):
    total = defaultdict(int)
    for address in set(addresses):
        for asset, amount in vectors[address].items():
            total[asset] += amount
    return total


rows = []
for item in nine:
    tx = item['tx']
    fact = facts[tx]
    transfers, withdrawals, deposits = [], [], []
    for log in prior[tx]['logs']:
        token, indexed = log['emitter'].lower(), log['indexed']
        if token != WETH:
            continue
        if log['name'].startswith('Transfer ') and '3' not in indexed:
            transfers.append({'token': token, 'from': indexed['1'].lower(), 'to': indexed['2'].lower(), 'raw': log['raw_words_uint'][0]})
        elif log['name'].startswith('Withdrawal '):
            withdrawals.append({'address': indexed['1'].lower(), 'raw': log['raw_words_uint'][0]})
        elif log['name'].startswith('Deposit '):
            deposits.append({'address': indexed['1'].lower(), 'raw': log['raw_words_uint'][0]})
    sender, receiver = item['from'], fact['protocol_reward_recipient']
    vectors = compute_vectors(sender, item['to'], int(item['top_value_wei']), int(item['gas_wei']), transfers, withdrawals, deposits, item['visible_native_flows'])
    unknown = class_map[tx]['other_terminal_distributions_not_claimed_same_entity']
    terminal_addresses = [x['to'] for x in unknown]
    selected = selected_sum(vectors, [sender, receiver] + terminal_addresses)
    gross = int(item['fixed_WETH_raw']) + int(item['variable_WETH_raw'])
    outward = sum(int(x['wei']) for x in class_map[tx]['known_external_native_payments_to_deduct'])
    arithmetic = gross - int(item['gas_wei']) - outward
    assert selected.get('ETH_wei', 0) + selected.get(WETH + '_raw', 0) == arithmetic, tx
    for key in ('from', 'gas_used'):
        if key == 'from':
            assert item[key] == fact[key]
    assert int(item['gas_wei']) == int(fact['gas_wei'])
    rows.append({'tx': tx, 'branch': 'WETH', 'gas_wei': item['gas_wei'], 'gross_protocol_WETH_raw': str(gross), 'specified_external_native_payments_wei': str(outward), 'conditional_available_after_specified_payments_and_gas_ETH_WETH_raw': str(arithmetic), 'conditional_available_ETH_WETH': str(Decimal(arithmetic) / 10**18), 'from': sender, 'reward_receiver': receiver, 'unknown_terminal_distributions': unknown, 'from_event_flow_vector': serialize(vectors[sender]), 'reward_receiver_event_flow_vector': serialize(vectors[receiver]), 'conditionally_combined_addresses': sorted(set([sender, receiver] + terminal_addresses)), 'conditionally_combined_event_flow_vector': serialize(selected), 'not_proven_same_entity_or_personal_profit': True, 'native_coverage': 'Existing HTML actual displayed rows, direct case additionally prior State; no independently complete trace claim', 'source_html': item['source_path'], 'source_html_sha256': item['source_sha256']})

for item in scope['fixed_items']:
    if item.get('full_tx_HTML'):
        continue
    tx = item['tx']
    response = json.loads((root / 'missing4' / (tx + '-receipt.original.json')).read_text())
    receipt = response.get('result')
    if not isinstance(receipt, dict):
        rows.append({'tx': tx, 'branch': item['branch'], 'receipt_status': 'UNRESOLVED_PROVIDER_ERROR', 'old_observed_gross_fixed_WETH_raw': item['fixed_WETH_raw'], 'old_observed_gross_collateral_raw': item['variable_collateral_raw'], 'gas_wei': None, 'native_flows': None, 'retention': 'UNKNOWN_NOT_ZERO'})
        continue
    transaction = json.loads((root / 'missing4' / (tx + '-transaction.original.json')).read_text())['result']
    native_response = json.loads((root / 'missing4' / (tx + '-native.original.json')).read_text())
    assert isinstance(native_response['result'], list)
    native = [{'from': x['from'].lower(), 'to': x['to'].lower(), 'wei': x['value']} for x in native_response['result'] if int(x['value']) != 0 and x['isError'] == '0']
    transfers, withdrawals, deposits = [], [], []
    event = event_map[tx]
    matching_events = [q for q in receipt['logs'] if q['address'].lower() == event['address'] and int(q['logIndex'], 16) == event['log_index']]
    assert len(matching_events) == 1
    words = [int(matching_events[0]['data'][offset:offset + 64], 16) for offset in range(2, len(matching_events[0]['data']), 64)]
    assert len(words) == 10 and words[2] == int(item['fixed_WETH_raw']) and words[3] == int(item['variable_collateral_raw'])
    for log in receipt['logs']:
        topics = log['topics']
        if topics[0] == TRANSFER and len(topics) == 3:
            transfers.append({'token': log['address'].lower(), 'from': '0x' + topics[1][-40:].lower(), 'to': '0x' + topics[2][-40:].lower(), 'raw': str(int(log['data'], 16)), 'log_index': int(log['logIndex'], 16)})
        elif log['address'].lower() == WETH and topics[0] in (WITHDRAW, DEPOSIT):
            target = withdrawals if topics[0] == WITHDRAW else deposits
            target.append({'address': '0x' + topics[1][-40:].lower(), 'raw': str(int(log['data'], 16))})
    fixed = [x for x in transfers if x['token'] == WETH and x['raw'] == item['fixed_WETH_raw']]
    assert len(fixed) == 1
    receiver, sender = fixed[0]['to'], transaction['from'].lower()
    gas = int(receipt['gasUsed'], 16) * int(receipt['effectiveGasPrice'], 16)
    top_value = int(transaction['value'], 16)
    vectors = compute_vectors(sender, transaction['to'].lower(), top_value, gas, transfers, withdrawals, deposits, native)
    foreign_tokens_out = [x for x in transfers if x['from'] == receiver and x['to'] not in (sender, receiver, '0x0000000000000000000000000000000000000000') and x['token'] == WETH]
    # Token payouts are not automatically profit, a bribe, or owned by the sender.
    terminal_addresses = [x['to'] for x in foreign_tokens_out]
    selected = selected_sum(vectors, [sender, receiver] + terminal_addresses)
    parity = selected.get('ETH_wei', 0) + selected.get(WETH + '_raw', 0)
    rows.append({'tx': tx, 'branch': item['branch'], 'from': sender, 'reward_receiver': receiver, 'top_value_wei': str(top_value), 'gas_wei': str(gas), 'gas_ETH': str(Decimal(gas) / 10**18), 'native_provider_status': native_response['status'], 'native_provider_message': native_response['message'], 'native_flows': native, 'erc20_transfer_events': transfers, 'WETH_withdrawal_events': withdrawals, 'WETH_deposit_events': deposits, 'from_event_flow_vector': serialize(vectors[sender]), 'reward_receiver_event_flow_vector': serialize(vectors[receiver]), 'unclassified_terminal_WETH_distributions': foreign_tokens_out, 'conditionally_combined_addresses': sorted(set([sender, receiver] + terminal_addresses)), 'conditionally_combined_event_flow_vector': serialize(selected), 'ETH_WETH_parity_component_only': str(Decimal(parity) / 10**18), 'not_proven_same_entity_or_personal_profit': True, 'nonETH_token_vectors_are_Transfer_event_net_not_independent_balance_snapshot': True, 'provider_empty_native_is_not_independent_absence_proof': len(native) == 0})

assert len(rows) == 13
weth_rows = [x for x in rows if x['branch'] == 'WETH']
gross9 = sum(int(x['gross_protocol_WETH_raw']) for x in weth_rows)
gas9 = sum(int(x['gas_wei']) for x in weth_rows)
out9 = sum(int(x['specified_external_native_payments_wei']) for x in weth_rows)
left9 = gross9 - gas9 - out9
known_gas = sum(int(x['gas_wei']) for x in rows if x.get('gas_wei') is not None)
result = {'at_utc': datetime.now(timezone.utc).isoformat(), 'status': 'PROVISIONAL_PENDING_INDEPENDENT_ARITHMETIC_REVIEW', 'fixed_successes': 13, 'complete_cost_originals': 12, 'unresolved_cost_originals': 1, 'transactions': rows, 'WETH9_summary': {'gross_protocol_WETH': str(Decimal(gross9) / 10**18), 'actual9gas_ETH': str(Decimal(gas9) / 10**18), 'specified_visible_external_native_payments_ETH': str(Decimal(out9) / 10**18), 'conditional_available_after_gas_and_specified_payments_ETH_WETH': str(Decimal(left9) / 10**18), 'outward_payments_over_gross_percent_not_ROI': str(Decimal(out9) / Decimal(gross9) * 100), 'label': 'Conditional aggregate over listed payer/rewardreceiver/terminaldistribution addresses, before unknown beneficiary allocation, other failures or operating costs; not actual From or all-entity profit or USD'}, 'actual12known_gas_ETH': str(Decimal(known_gas) / 10**18), 'whole13_net_profit': 'UNKNOWN', 'future_personal_capture_capacity_or_wealth_proved': False, 'no_new_price_model_backtest_EVM_strategy_or_trade': True, 'limits': ['ETH/WETH1:1 quantity only, no actual unwrap/swap by researcher', 'Known historical swaps accounted only from actual recorded token/native flows, not a simulated quote', 'Unknown terminal recipients do not imply common ownership or a bribe', '13 successful events omit unsuccessful attempts of all other operators; existing seven-attempt six-failure case is unchanged', 'Same provider records and historical explorer originals do not independently prove complete chain/state coverage']}
(root / 'success-retention-accounting-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('WETH9_summary', 'actual12known_gas_ETH', 'whole13_net_profit')}, indent=2))
for row in rows:
    print(json.dumps({key: row.get(key) for key in ('tx', 'branch', 'conditional_available_ETH_WETH', 'ETH_WETH_parity_component_only', 'from_event_flow_vector', 'conditionally_combined_event_flow_vector', 'retention')}, ensure_ascii=False))
