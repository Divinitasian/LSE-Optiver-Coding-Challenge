from math import isclose
from datetime import datetime
from datetime import datetime
from optibook.common_types import PriceVolume, Instrument, OrderStatus

from optistrats.strats.market_maker import *


def test_action():
    instrument = Instrument("sample", tick_size=0.1)
    snapshot = PriceBook(
        timestamp=datetime.now(),
        instrument_id=instrument.instrument_id,
        bids=[
            PriceVolume(100, 2),
            PriceVolume(95, 100),
        ],
        asks=[
            PriceVolume(101, 1),
            PriceVolume(105, 300),
        ]
    )

    agent = MarketMaker(
        instrument, 
        position_limit=100        
    )

    # neutral position
    bid_order, ask_order = agent.action(
        0, 
        snapshot
    )
    assert isclose(bid_order.price, 95.1, abs_tol=0.4)
    assert isclose(ask_order.price, 104.9, abs_tol=0.4)

    # limit position
    bid_order, ask_order = agent.action(
        -100, 
        snapshot
    )
    assert isclose(bid_order.price, 105.0, abs_tol=0.4)
    assert isclose(ask_order.price, 115.0, abs_tol=0.4)

    bid_order, ask_order = agent.action(
        100, 
        snapshot
    )
    assert isclose(bid_order.price, 85.0, abs_tol=0.4)
    assert isclose(ask_order.price, 95.0, abs_tol=0.4)
    


    