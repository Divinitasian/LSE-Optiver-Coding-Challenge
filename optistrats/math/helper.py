from typing import List
from math import floor, ceil
from optibook.common_types import PriceVolume, PriceBook


def round_down_to_tick(price, tick_size)-> float:
    """
    Rounds a price down to the nearest tick, e.g. if the tick size is 0.10, a price of 0.97 will get rounded to 0.90.
    """
    return floor(price / tick_size) * tick_size


def round_up_to_tick(price, tick_size)-> float:
    """
    Rounds a price up to the nearest tick, e.g. if the tick size is 0.10, a price of 1.34 will get rounded to 1.40.
    """
    return ceil(price / tick_size) * tick_size

def format_order_price(
    postive_price: float,
    side: str,
    tick_size: float
) -> float:
    """Format the order price using tick size

    Parameters
    ----------
    price
        the unformatted price. Assume to be positive.
        Negative price will throw an AssertionError.
    side
        bid or ask
    tick_size
        minimum price change

    Returns
    -------
        the formatted price. Should be multiple of tick size.
        And bid always round down and ask always round up
    """
    assert postive_price > 0
    if side == 'bid':
        return round_down_to_tick(postive_price, tick_size)
    else:
        return round_up_to_tick(postive_price, tick_size)
    
def get_vwap(price_volume_list: List[PriceVolume]) -> float:
    try:
        n = 0
        d = 0
        for pv in price_volume_list:
            n += pv.price * pv.volume
            d += pv.volume
        return n/d
    except:
        raise ValueError(f"price_volume_list={price_volume_list} in valid.")
    
def get_mid_vwap(snapshot: PriceBook):
    bid_vwap = get_vwap(snapshot.bids)
    ask_vwap = get_vwap(snapshot.asks)
    return (bid_vwap + ask_vwap) / 2
    
def get_spread_vwap(snapshot: PriceBook):
    bid_vwap = get_vwap(snapshot.bids)
    ask_vwap = get_vwap(snapshot.asks)
    spread = ask_vwap - bid_vwap
    if spread > 0:
        return ask_vwap - bid_vwap
    else:
        raise ValueError(f"negative spread with price book snapshot={snapshot}.")
