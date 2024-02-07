from optibook.synchronous_client import Exchange
from optistrats.utils.data import *

exchange = Exchange()
exchange.connect()

def test_database():
    db = DataBase(exchange)
    db.fetch()
    instruments = db.get_instruments()
    instrument = instruments[7]
    db.get_tradable_instruments()
    db.get_position(instrument)
    db.get_last_price_book(instrument)
    db.get_outstanding_order(instrument)
    db.fetch()