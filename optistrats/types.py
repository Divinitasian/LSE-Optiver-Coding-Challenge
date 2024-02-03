from optibook.common_types import Instrument

class PreOrder:
    """
    Summary of an order.

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
    """
    def __init__(
        self, 
        instrument: Instrument, 
        price: float, 
        volume: int, 
        side: str
    ):
        self.instrument = instrument
        self.price = price
        self.volume = volume
        self.side = side

    def __repr__(self):
        return f'PreOrder(instrument_id={self.instrument.instrument_id}, price={self.price}, ' \
               f'volume={self.volume}, side={self.side})'
