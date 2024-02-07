from datetime import datetime

from optibook.synchronous_client import Exchange
from optistrats.utils.data import *

exchange = Exchange()
exchange.connect()

def test_database():
    db = DataBase(exchange)
    db.fetch()
    instruments = db.get_instruments()
    instrument = instruments[7]
    print(db.get_tradable_instruments())
    print(db.get_position(instrument))
    print(db.get_last_price_book(instrument))
    print(db.get_outstanding_order(instrument))
    db.fetch()

    
def test_db_speedup():
    db = DataBase(exchange)
    instruments = db.get_instruments()
    instrument = instruments[7]
    n_repeats = 100

    # db
    start = datetime.now()
    for _ in range(n_repeats):
        db.get_last_price_book(instrument)

    db_es = datetime.now() - start
    print(f"\nDB: escaped time - {db_es}.")

    # exchange
    start = datetime.now()
    for _ in range(n_repeats):
        exchange.get_last_price_book(instrument.instrument_id)

    ex_es = datetime.now() - start
    print(f"Exchange: escaped time - {ex_es}.")
    
    print(f"Speedup: {ex_es // db_es}.")

    