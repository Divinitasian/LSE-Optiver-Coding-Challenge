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
    try:
        price = 0
        format_order_price(price, 'bid', tick_size)
        assert False
    except:
        assert True
