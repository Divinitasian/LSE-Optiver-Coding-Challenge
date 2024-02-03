"""
The narrow-spread strategy.
"""
import typing
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

    def set_volume(self, value: int, side: str) -> None:
        is_valid = isinstance(value, int) and (0 < value < 100)
        if not is_valid:
            raise ValueError(f"cannot set value={value}.")
        
        if side == 'bid':
            self.bid_volume = value
        elif side == 'ask':
            self.ask_volume = value
        else:
            raise ValueError(f"{side} side not supported. Choose bid or ask.")

    def set_risk_premium(self, value: float) -> None:
        is_valid = isinstance(value, float) and value > 0
        if not is_valid:
            raise ValueError(f"cannot set risk premium={value}.")
        self.risk_premium = value

    def action(self, best_bid, best_ask) -> typing.Tuple[OrderStatus]:
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
