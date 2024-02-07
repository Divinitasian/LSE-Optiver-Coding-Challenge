from math import isclose
from datetime import datetime
from datetime import datetime
from optibook.common_types import PriceVolume

from optistrats.strats.market_maker import *
from optistrats.types import sample_instrument


def test_action():
    snapshot = PriceBook(
        timestamp=datetime.now(),
        instrument_id= sample_instrument.instrument_id,
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
        sample_instrument, 
        position_limit=100        
    )

    # neutral position
    bid_order, ask_order = agent.action(
        0, 
        snapshot
    )
    assert bid_order.price_in_ticksize == 951
    assert ask_order.price_in_ticksize == 1049

    # limit position
    bid_order, ask_order = agent.action(
        -100, 
        snapshot
    )
    assert bid_order.price_in_ticksize == 1050
    assert ask_order.price_in_ticksize == 1148

    bid_order, ask_order = agent.action(
        100, 
        snapshot
    )
    assert bid_order.price_in_ticksize == 853
    assert ask_order.price_in_ticksize == 950
    