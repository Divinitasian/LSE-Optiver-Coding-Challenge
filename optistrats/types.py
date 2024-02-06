from optibook.common_types import Instrument, OrderStatus
from optistrats.math.helper import round_to_tick

class LimitOrder:	
    """	
    Hashable limit order

    Attributes	
    ----------	
    instrument_id: str	
        The id of the traded instrument.	
    price_in_ticksize: int	
        The price in tick size.	
    volume: int	
        The volume that was traded.	
    side: 'bid' or 'ask'	
        If 'bid' this is a bid order.	
        If 'ask' this is an ask order.		
    """	
    def __init__(	
        self, 	
        instrument: Instrument, 	
        price_in_ticksize: int, 	
        volume: int, 	
        side: str
    ):	
        self.instrument = instrument	
        self.price_in_ticksize = price_in_ticksize
        self.volume = volume	
        self.side = side	

    def __repr__(self):	
        return f'LimitOrder(instrument_id={self.instrument.instrument_id}, price_in_ticksize={self.price_in_ticksize}, volume={self.volume}, side={self.side})'	

    def __eq__(self, other) -> bool:
        # with limit order
        if isinstance(other, LimitOrder):
            return (self.instrument.instrument_id == other.instrument.instrument_id) and  \
                (self.side == other.side) and \
                    (self.price_in_ticksize == other.price_in_ticksize)
        # with order status
        elif isinstance(other, OrderStatus):
            return (self.instrument.instrument_id == other.instrument_id) and  \
                (self.side == other.side) and \
                (self.price_in_ticksize == round_to_tick(other.price, self.instrument.tick_size, self.side))
        
    def __hash__(self) -> int:
        return hash(
            (
                self.instrument.instrument_id,
                self.price_in_ticksize,
                self.side
            )
        )
