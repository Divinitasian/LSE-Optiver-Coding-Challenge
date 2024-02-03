"""
The narrow-spread strategy.
"""
import typing
from optibook.common_types import Instrument
from optistrats.types import PreOrder
from optistrats.utils import TICK_SIZE, INITIAL_VOLUME

class MarketMaker:
    def __init__(
        self, 
        instrument: Instrument,
        volume: int = INITIAL_VOLUME,
        risk_premium: float = TICK_SIZE
    ) -> None:
        self.instrument = instrument
        self.volume = volume
        self.risk_premium = risk_premium

    def action(self, best_bid: float, best_ask: float) -> typing.Tuple[PreOrder]:
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
        margin = self.risk_premium if spread > 2 * self.risk_premium else 0
        return (
            PreOrder(
                instrument=self.instrument,
                price=best_bid+margin,
                volume=self.volume,
                side='bid'
            ), 
            PreOrder(
                instrument=self.instrument,
                price=best_ask-margin,
                volume=self.volume,
                side='ask'
            )
        )
