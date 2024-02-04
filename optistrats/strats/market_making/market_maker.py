from optibook.common_types import Instrument, PriceBook
from optistrats.utils.math import format_order_price, get_mid_vwap, get_spread_vwap
from optistrats.types import TraderOrder

class MarketMaker:
    def __init__(
        self, 
        instrument: Instrument,
        init_position: int
    ) -> None:
        self.instrument = instrument
        self.position = init_position

    def action(
        self,
        snapshot: PriceBook
    ) -> float:
        mid = get_mid_vwap(snapshot)
        spread = get_spread_vwap(snapshot)
        bid = format_order_price(
            mid - spread / 2, 'bid', self.instrument.tick_size
        )
        ask = format_order_price(
            mid + spread / 2, 'ask', self.instrument.tick_size
        )
        volume = 10
        return (
            TraderOrder(
                self.instrument,
                bid,
                volume,
                'bid',
                'limit'
            ),
            TraderOrder(
                self.instrument,
                ask,
                volume,
                'ask',
                'limit'
            )
        )
