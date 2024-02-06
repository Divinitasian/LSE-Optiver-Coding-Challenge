from typing import Iterable
from math import floor, ceil
from optibook.common_types import PriceVolume, PriceBook


def round_to_tick(
    price: float, 
    tick_size: float,
    side: str,
    to_ticksize: bool = True
):
    """Rounds a price down to the nearest tick.
    
    E.g., if the tick size is 0.10, a price of 0.97 will get rounded to 0.90 or 9.

    Parameters
    ----------
    price
        raw price in dollars
    tick_size
        the minimum price change unit
    side
        bid: round down, ask: round up
    to_ticksize, optional
        format the price as base point in the tick size, by default True

    Returns
    -------
        price or base points
    """
    ratio = price / tick_size
    bsp = floor(ratio) if side == "bid" else ceil(ratio)
    if to_ticksize:
        return bsp
    return  bsp * tick_size


def get_vwap(price_volumes: Iterable[PriceVolume]) -> float:
    """Compute the volume weighted adjusted price for a sequence of (price, volume) paris

    Parameters
    ----------
    price_volumes
        a sequence of price, volume

    Returns
    -------
        the weighted average of price with the volume being the weights
    """
    n = 0
    d = 0
    for pv in price_volumes:
        n += pv.price * pv.volume
        d += pv.volume
    return n/d
    

def get_mid_vwap(snapshot: PriceBook):
    bid_vwap = get_vwap(snapshot.bids)
    ask_vwap = get_vwap(snapshot.asks)
    mid = (bid_vwap + ask_vwap) / 2
    if mid < 0:
        raise ValueError(f"negative mid with price book snapshot={snapshot}.")
    return mid
    
def get_spread_vwap(snapshot: PriceBook):
    bid_vwap = get_vwap(snapshot.bids)
    ask_vwap = get_vwap(snapshot.asks)
    spread = ask_vwap - bid_vwap
    if spread < 0:
        raise ValueError(f"negative spread with price book snapshot={snapshot}.")
    return spread
        
