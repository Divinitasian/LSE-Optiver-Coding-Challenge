from typing import Tuple
from optibook.common_types import Instrument, PriceBook

from optistrats.types import LimitOrder
from optistrats.math.helper import round_to_tick, get_mid_vwap, get_spread_vwap


class MarketMaker:
    def __init__(
        self, 
        instrument: Instrument,
        position_limit: int = 100,
    ) -> None:
        self.instrument = instrument
        self.position_limit = position_limit

    def get_fair_value(
        self,
        snapshot: PriceBook
    ) -> float:
        mid = get_mid_vwap(snapshot)
        return mid
    
    def get_position_penalty(
        self,
        position: int,
        snapshot: PriceBook
    ) -> float:
        """Compute the penalty based on current position

        When position is 0, the bid = -.5 spread, and the ask = + 0.5 spread => mid = 0 => penalty = 0
        When position is 1, the ask = -0.5 spread => mid = -spread => penalty = -spread
        When position is -1 the bid = + 0.5 spread => mid = spread => penalty = + spread

        Parameters
        ----------
        position
            position value
        snapshot
            the current orderbook

        Returns
        -------
            a penalty to be added on the fair value when construct the mid
        """
        pct = position / self.position_limit
        penalty = pct * get_spread_vwap(snapshot)
        return penalty

    def get_spread(
        self,
        snapshot: PriceBook
    ) -> float:
        spread = get_spread_vwap(snapshot)
        spread -= 2 * self.instrument.tick_size
        return spread

    def action(
        self,
        position: int,
        snapshot: PriceBook
    ) -> Tuple[LimitOrder]:
        # construct the mid
        mid = self.get_fair_value(snapshot)
        mid -= self.get_position_penalty(position, snapshot)
        # compute the spread
        spread = self.get_spread(snapshot)
        # build the limit orders
        bid = round_to_tick(
            mid - spread / 2, self.instrument.tick_size, 'bid' 
        )
        ask = round_to_tick(
            mid + spread / 2, self.instrument.tick_size, 'ask'
        )
        
        volume = 10

        return (
            LimitOrder(
                self.instrument,
                bid,
                volume,
                'bid'
            ),
            LimitOrder(
                self.instrument,
                ask,
                volume,
                'ask'
            )
        )
    