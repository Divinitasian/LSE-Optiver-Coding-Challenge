from optistrats.strats.narrow_spread import MarketMaker as NSMarketMaker
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()
all_instruments = exchange.get_instruments()
all_instrument_ids = all_instruments.keys()

# select the first instrument
instrument = all_instruments[all_instrument_ids[0]]
agent = NSMarketMaker(
    instrument,
)

def test_set_volume():
    assert False

def test_set_risk_premium():
    assert False

def test_action():
    assert False