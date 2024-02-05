import math
from optibook.common_types import Instrument, OrderStatus

class TraderOrder:
    """
    Summary of an order from the trader.

    Attributes
    ----------
    instrument_id: str
        The id of the traded instrument.

    price: float
        The price at which the instrument traded.

    volume: int
        The volume that was traded.

    side: 'bid' or 'ask'
        If 'bid' this is a bid order.
        If 'ask' this is an ask order.

    order_type: str
        'limit' or 'ioc'
    """
    def __init__(
        self, 
        instrument: Instrument, 
        price: float, 
        volume: int, 
        side: str,
        order_type: str
    ):
        self.instrument = instrument
        self.price = price
        self.volume = volume
        self.side = side
        self.order_type = order_type

    def __repr__(self):
        return f'PreOrder(instrument_id={self.instrument.instrument_id}, price={self.price}, ' \
               f'volume={self.volume}, side={self.side}, order_type={self.order_type})'
    
    def __eq__(self, other: OrderStatus):
        return (self.side == other.side) and math.isclose(
            self.price, other.price, abs_tol=self.instrument.tick_size
        )
