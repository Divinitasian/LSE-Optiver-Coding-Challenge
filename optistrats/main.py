import threading
from optibook.synchronous_client import Exchange
from optistrats.strats.market_maker import MarketMaker
from optistrats.utils.execution import ExecutionTrader
from optistrats.utils.data import DataBase
from optistrats.strats.strategy import market_making

def main():
    exchange = Exchange()
    exchange.connect()

    database = DataBase(exchange)

    instrument = exchange.get_instruments()['OB5X_ETF']
    market_maker = MarketMaker(instrument)
    execution_trader = ExecutionTrader(instrument)

    data_thread = threading.Thread(
        target=database.run,
        kwargs={'verbose': True},
        name="Database"
    )
    
    strats_thread = threading.Thread(
        target=market_making, 
        name=instrument.instrument_id,
        args=(
            database,
            market_maker,
            execution_trader,
            exchange,
        ),
        kwargs={"rest_in_secs": 0.2}
    )

    data_thread.start()
    # strats_thread.start()

    # strats_thread.join()
    data_thread.join()


if __name__ == "__main__":
    main()
    
