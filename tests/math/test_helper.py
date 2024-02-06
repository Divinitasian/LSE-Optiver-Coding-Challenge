from math import isclose
from optibook.common_types import PriceVolume
from optistrats.math.helper import *

def test_format_order_price():
    price = 102.363
    tick_size = 0.1
    bid_price = 102.3
    ask_price = 102.4
    assert isclose(
        format_order_price(price, 'bid', tick_size),
        bid_price
    ) 
    assert isclose(
        format_order_price(price, 'ask', tick_size),
        ask_price
    )

def test_get_vwap():
    l = [
        PriceVolume(1, 4),
        PriceVolume(4, 5)
    ]
    ans = 8/3
    assert isclose(get_vwap(l), ans)
    l = []
    try:
        get_vwap(l)
        assert False
    except Exception as e:
        print(e)
        assert True 
