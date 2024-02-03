import numpy
from optistrats.strats.narrow_spread import MarketMaker as NSMarketMaker
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()
all_instruments = list(exchange.get_instruments().values())

# select the first instrument
instrument = all_instruments[0]
agent = NSMarketMaker(
    instrument,
)

def test_action():
    non_cross_bid, non_cross_ask = 0.2, 0.6
    bid_order, ask_order = agent.action(non_cross_bid, non_cross_ask)
    assert numpy.isclose(bid_order.price, 0.3) 
    assert numpy.isclose(ask_order.price, 0.5)

    cross_bid, cross_ask = 0.2, 0.4
    bid_order, ask_order = agent.action(cross_bid, cross_ask)
    assert numpy.isclose(bid_order.price, 0.2) 
    assert numpy.isclose(ask_order.price, 0.4)
