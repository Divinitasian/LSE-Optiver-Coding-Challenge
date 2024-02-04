"""
Make the portfolio delta-neutral.
"""
from typing import Dict
from optibook.common_types import Instrument
from optistrats.types import TraderOrder
from optistrats.utils import MAX_BUYING_PRICE, MIN_SELLING_PRICE

class RiskManager:
    def __init__(self, base_instrument: Instrument) -> None:
        pass

    def action(
        self, 
        related_positions: Dict[Instrument, int], 
        base_instrument_price: float
    ) -> TraderOrder:
        pass
