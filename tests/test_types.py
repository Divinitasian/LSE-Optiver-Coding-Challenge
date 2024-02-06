from collections import Counter
from optibook.common_types import OrderStatus

from optistrats.types import *

instrument = Instrument("sample", tick_size=0.1)

def test_eq():
    
    bid_order = OrderStatus()
    bid_order.instrument_id = instrument.instrument_id
    bid_order.price = 100.23
    bid_order.volume = 100
    bid_order.side = 'bid'
    
    
    bid_limit_order = LimitOrder(
        instrument,
        price_in_ticksize=1002,
        volume=52,
        side='bid'
    )
    assert bid_limit_order == bid_order
    

    ask_limit_order = LimitOrder(
        instrument,
        price_in_ticksize=1002,
        volume=52,
        side='ask'
    )

    assert ask_limit_order != bid_limit_order

    ask_order = OrderStatus()
    ask_order.instrument_id = instrument.instrument_id
    ask_order.price = 100.16
    ask_order.volume = 100
    ask_order.side = 'ask'

    assert ask_limit_order == ask_order


def test_hashable():
    bid_limit_order = LimitOrder(
        instrument,
        price_in_ticksize=1002,
        volume=52,
        side='bid'
    )
    
    ask_limit_order = LimitOrder(
        instrument,
        price_in_ticksize=1002,
        volume=52,
        side='ask'
    )

    counter = Counter({
        bid_limit_order: 1,
        ask_limit_order: 1
    })

    assert counter[bid_limit_order] == 1
    


