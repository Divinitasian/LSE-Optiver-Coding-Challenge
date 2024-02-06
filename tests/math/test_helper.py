from math import isclose
from optibook.common_types import PriceVolume
from optistrats.math.helper import *

def test_round_to_tick():
    price = 102.363
    tick_size = 0.1
    bid_price, bid_price_in_bsp = 102.3, 1023
    ask_price, ask_price_in_bsp = 102.4, 1024


    assert round_to_tick(price, tick_size, 'bid') == bid_price_in_bsp
    assert round_to_tick(price, tick_size, 'ask') == ask_price_in_bsp

    # to_bsp = False
    assert isclose(
        round_to_tick(price, tick_size, 'bid', to_ticksize=False),
        bid_price
    ) 
    assert isclose(
        round_to_tick(price, tick_size, 'ask', to_ticksize=False),
        ask_price
    )


def test_get_vwap():
    l = [
        PriceVolume(1, 4),
        PriceVolume(4, 5)
    ]
    ans = 8/3
    assert isclose(get_vwap(l), ans)
