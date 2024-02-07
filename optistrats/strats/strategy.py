import os
import time
import logging
from optibook.synchronous_client import Exchange
from optistrats.strats.market_maker import MarketMaker
from optistrats.utils.execution import ExecutionTrader
from optistrats.utils.data import DataBase

def market_making(
    database: DataBase,
    market_maker: MarketMaker,
    execution_trader: ExecutionTrader,
    exchange: Exchange,
    rest_in_secs: float
) -> None:
    """Market making strategy.
    
    0. The database provides the current market state.
    1. The market maker decides the limit orders.
    2. The execution traders decides the old orders to cancel and the new orders to insert.
    3. Send orders to the exchange

    Parameters
    ----------
    database
        The local database that stores the information from the exchange.
    market_maker
        The object of `MarketMaker` class.
    execution_trader
        The object of `ExecutionTrader` class.
    exchange
        The exchange connected client.
    rest_in_secs
        The sleep time after each iteration to control the speed of sending orders to exchange.
    """
    while True:
        # preceive the market
        instrument = market_maker.instrument
        position = database.get_position(instrument)
        snapshot = database.get_last_price_book(instrument)
        outstanding_orders = database.get_outstanding_order(instrument)
        try:
            # market maker
            trader_orders = market_maker.action(
                position,
                snapshot
            )
            # execution trader
            execution_trader.minimize_cost(
                trader_orders,
                outstanding_orders
            )
            # send to exchange
            order_ids = execution_trader.cancel_orders()
            exchange.delete_orders(order_ids)
            for order in execution_trader.insert_orders():
                exchange.insert_order(
                    instrument.instrument_id,
                    price=order.price,
                    volume=order.volume,
                    side=order.side,
                    order_type=order.order_type
                )
        except:
            logging.info("Skip.")
        finally:
            time.sleep(rest_in_secs)
        
        

