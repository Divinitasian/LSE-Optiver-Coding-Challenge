import time
from optibook.synchronous_client import Exchange
from optistrats.strats.market_making.market_maker import MarketMaker
from optistrats.execution import ExecutionTrader
from optistrats.data import DataBase


def market_making(
    database: DataBase,
    market_maker: MarketMaker,
    execution_trader: ExecutionTrader,
    exchange: Exchange,
    rest_in_secs: float
) -> None:
    while True:
        # preceive the market
        instrument = market_maker.instrument
        position = database.get_position(instrument)
        snapshot = database.get_last_price_book(instrument)
        outstanding_orders = database.get_outstanding_order(instrument)
        # market maker
        trader_orders = market_maker.action(
            position,
            snapshot
        )
        # execution trader
        execution_trader.action(
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
        time.sleep(rest_in_secs)
        
        

