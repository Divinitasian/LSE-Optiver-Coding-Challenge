"""
The narrow-spread strategy.
"""

from optibook.common_types import Instrument, OrderStatus
from optistrats.utils import TICK_SIZE, INITIAL_VOLUME

class MarketMaker:
    def __init__(
        self, 
        instrument: Instrument,
        bid_volume: int = INITIAL_VOLUME,
        ask_volume: int = INITIAL_VOLUME,
        risk_premium: float = TICK_SIZE
    ) -> None:
        self.instrument = instrument
        self.bid_volume = bid_volume
        self.ask_volume = ask_volume
        self.risk_premium = risk_premium

    def set_bid_volume(self, value) -> None:
        self.bid_volume = value
    
    def set_ask_volume(self, value) -> None:
        self.ask_volume = value

    def set_risk_premium(self, value) -> None:
        self.risk_premium = value

    def action(self, best_bid, best_ask) -> tuple:
        """If the spread is large, we narrow it. Otherwise, we join it.

        Parameters
        ----------
        best_bid
            the highest bid price in the current market
        best_ask
            the lowest ask price in the current market

        Returns
        -------
            (bid_order, ask_order)
        """
        spread = best_ask - best_bid
        margin = self.risk_premium if spread > 2 * TICK_SIZE else 0
        return (
            OrderStatus(
                order_id=-1,
                instrument_id=self.instrument.instrument_id,
                price=best_bid+margin,
                volume=self.bid_volume,
                side='bid'
            ), 
            OrderStatus(
                order_id=-1,
                instrument_id=self.instrument.instrument_id,
                price=best_ask-margin,
                volume=self.ask_volume,
                side='ask'
            )
        )
