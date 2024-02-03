"""
Manage the risk: delta and positions.
"""
from typing import Dict
from optibook.common_types import Instrument
from optistrats.types import PreOrder
from optistrats.utils import MAX_BUYING_PRICE, MIN_SELLING_PRICE

class RiskManager:
    def __init__(self, base_instrument) -> None:
        pass

    def action(
        self, 
        positions: Dict[Instrument, int], 
        base_instrument_price: float
    ) -> PreOrder:
        pass
