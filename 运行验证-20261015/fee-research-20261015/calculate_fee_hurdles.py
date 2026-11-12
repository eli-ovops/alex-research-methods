"""Teaching arithmetic for public HK fees; no market connection or model execution."""
from decimal import Decimal as D, ROUND_CEILING
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parent
P = D('342.96')  # Prior issuer-page close, a reference price, not an executable quote.
CENT = D('0.01')


def cent_up(x):
    # Explicit illustrative convention. Actual broker rounding remains UNKNOWN.
    return x.quantize(CENT, rounding=ROUND_CEILING)


def order_fees(qty, price, plan, side):
    q, n = D(qty), D(qty) * price
    if plan == 'standard':
        commission = D(0)
        platform = max(D('1.88'), min(q * D('.009'), n * D('.01')))
    elif plan == 'conditional_promotion':
        assert price >= 100
        commission, platform = D(0), D('.99')
    elif plan == 'trader_regular':
        commission = D(0)
        platform = max(D(1), min(q * D('.005'), n * D('.01')))
    elif plan == 'pro':
        # None of this report's quantities reaches the conflicting cap/min case.
        commission = min(max(q * D('.01'), D(1)), n * D('.005'))
        platform = min(max(q * D('.009'), D('2.88')), n * D('.005'))
    elif plan == 'algorithm_note_if_applicable':
        commission, platform = n * D('.001'), D(0)
    else:
        raise ValueError(plan)
    fees = {
        'commission': commission,
        'platform': platform,
        'settlement': min(max(q * D('.003'), D('.01')), n * D('.03')),
        'sec': max(n * D('.0000206'), D('.01')) if side == 'sell' else D(0),
        'taf': D(0),  # Current HK main page / 2026-Q4 only. Not a permanent rule.
        'cat': max(q * D('.000003'), D('.01')),
    }
    rounded = {key: cent_up(value) for key, value in fees.items()}
    return {
        'side': side,
        'notional': str(n),
        'unrounded_components_usd': {k: str(v) for k, v in fees.items()},
        'illustrative_rounded_components_usd': {k: str(v) for k, v in rounded.items()},
        'unrounded_total_usd': str(sum(fees.values())),
        'illustrative_total_usd': str(sum(rounded.values())),
    }


def same_price_round_trip(q, plan):
    buy = order_fees(q, P, plan, 'buy')
    sell = order_fees(q, P, plan, 'sell')
    total = D(buy['illustrative_total_usd']) + D(sell['illustrative_total_usd'])
    notional = D(q) * P
    return {
        'plan': plan, 'qty': q, 'reference_price_usd': str(P),
        'one_way_notional_usd': str(notional), 'buy': buy, 'sell': sell,
        'illustrative_round_trip_cost_usd': str(total),
        'cost_over_one_way_notional_bp': str(total / notional * 10000),
        'unrounded_formula_total_usd': str(D(buy['unrounded_total_usd']) + D(sell['unrounded_total_usd'])),
        'exact_break_even_price': None,
        'note': 'Same-price fee ruler, not exact break-even, not trading P&L.',
    }


def main():
    plans = [same_price_round_trip(14, p) for p in (
        'standard', 'conditional_promotion', 'trader_regular', 'pro',
        'algorithm_note_if_applicable')]
    sizes = []
    for budget in (D('500'), D('5000'), D('50000'), D('500000')):
        q = int(budget / P)
        example = same_price_round_trip(q, 'standard')
        example['hypothetical_budget_usd'] = str(budget)
        example['unspent_before_fees_usd'] = str(budget - P * q)
        sizes.append(example)
    main_cost = D(plans[0]['cost_over_one_way_notional_bp'])
    # Extra execution drag is arbitrary scenario arithmetic, not measured spread/slippage.
    stress = []
    for extra_bp in (D(0), D(5), D(10), D(20)):
        stress.append({'assumed_total_round_trip_spread_slippage_bp': str(extra_bp),
                       'combined_same_price_cost_ruler_bp': str(main_cost + extra_bp),
                       'execution_drag_measured': False})
    result = {
        'calculated_at_utc': datetime.now(timezone.utc).isoformat(),
        'kind': 'teaching_arithmetic_only',
        'account_entity_user_confirmed': 'Hong Kong', 'actual_fee_plan': 'UNKNOWN',
        'reference_quote_source_receipt': '../endpoint-observation-20261015/issuer-price-cross-check.json',
        'reference_price_is_executable': False,
        'rounding': 'Each non-negative component rounded upward to cents for this teaching example only; actual rule UNKNOWN.',
        'assumptions': ['One cash buy and one cash sell, two orders, same reference price on both sides.',
                        'Whole shares, USD cash already available, no leverage, short borrow, FX or corporate action.',
                        'No split-fill aggregation or broker-specific customer arrangement is assumed.',
                        'All account-specific eligibility remains conditional; no plan switch performed.',
                        'TAF=0 applies to the currently observed 2026-Q4 fee schedule, not all historical trades.'],
        'not_included': ['measured bid-ask spread', 'measured slippage', 'market impact',
                         'opportunity cost', 'FX', 'financing', 'short borrow',
                         'tax on investment income', 'data/compute/software overhead'],
        'plan_examples': plans, 'size_examples_standard': sizes,
        'execution_drag_scenarios': stress,
        'proves_predictive_edge': False, 'proves_profitability': False,
        'proves_strategy_capacity': False, 'model_run': False, 'account_connected': False,
        'trades_placed': 0, 'new_paid_resources': 0,
    }
    target = ROOT / 'teaching-cost-ledger.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for x in plans:
        print(x['plan'], 'round_trip_usd=' + x['illustrative_round_trip_cost_usd'],
              'bp=' + str(round(D(x['cost_over_one_way_notional_bp']), 4)))
    for x in sizes:
        print('budget=' + x['hypothetical_budget_usd'], 'q=' + str(x['qty']),
              'round_trip_usd=' + x['illustrative_round_trip_cost_usd'],
              'bp=' + str(round(D(x['cost_over_one_way_notional_bp']), 4)))


if __name__ == '__main__':
    main()
