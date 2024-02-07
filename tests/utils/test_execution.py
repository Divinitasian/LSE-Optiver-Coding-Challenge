from optibook.common_types import OrderStatus
from optistrats.utils.execution import *
from optistrats.types import LimitOrder, sample_instrument

def test_receive():
    limit_orders = [
        LimitOrder(
            sample_instrument,
            price_in_ticksize=1235,
            volume=v,
            side='bid'
        ) for v in range(10, 100)
    ] + [
        LimitOrder(
            sample_instrument,
            price_in_ticksize=1235,
            volume=v,
            side='ask'
        ) for v in range(10, 100)
    ]

    outstanding_orders = {
        123: OrderStatus(),
        456: OrderStatus()
    }
    
    outstanding_orders[123].instrument_id = sample_instrument.instrument_id
    outstanding_orders[123].order_id = 123
    outstanding_orders[123].price = 123.5
    outstanding_orders[123].volume = 10
    outstanding_orders[123].side = 'bid'
    
    outstanding_orders[456].instrument_id = sample_instrument.instrument_id
    outstanding_orders[456].order_id = 456
    outstanding_orders[456].price = 123.6
    outstanding_orders[456].volume = 10
    outstanding_orders[456].side = 'ask'


    execution_trader = ExecutionTrader(sample_instrument)

    execution_trader.minimize_cost(limit_orders, outstanding_orders)
    assert execution_trader.cancel_orders() == [456]
    assert str(execution_trader.insert_orders()[0]) == \
        str(LimitOrder(
            sample_instrument,
            price_in_ticksize=1235,
            volume=10,
            side='ask'
        ).to_order_status())
