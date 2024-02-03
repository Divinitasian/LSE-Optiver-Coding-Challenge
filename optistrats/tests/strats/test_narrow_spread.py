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
    try:
        agent.set_volume(-1, side='bid')
    except ValueError:
        assert True
    value = 30
    agent.set_volume(value, side='ask')
    assert agent.ask_volume == value

def test_set_risk_premium():
    assert False

def test_action():
    assert False