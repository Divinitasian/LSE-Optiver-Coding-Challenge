import time
from optibook.synchronous_client import Exchange
from optistrats.utils.constants import MIN_SELLING_PRICE, MAX_BUYING_PRICE


def clear_position(exchange):
    positions = exchange.get_positions()
    pnl = exchange.get_pnl()
    
    print(f'Positions before: {positions}')
    print(f'\nPnL before: {pnl:.2f}')
    
    print(f'\nTrading out of positions')
    for iid, pos in positions.items():
        if pos > 0:
            print(f'-- Inserting sell order for {pos} lots of {iid}, with limit price {MIN_SELLING_PRICE:.2f}')
            exchange.insert_order(iid, price=MIN_SELLING_PRICE, volume=pos, side='ask', order_type='ioc')
        elif pos < 0:
            print(f'-- Inserting buy order for {abs(pos)} lots of {iid}, with limit price {MAX_BUYING_PRICE:.2f}')
            exchange.insert_order(iid, price=MAX_BUYING_PRICE, volume=-pos, side='bid', order_type='ioc')
        else:
            print(f'-- No initial position in {iid}, skipping..')
        
        time.sleep(0.10)
    
    time.sleep(1.0)
    
    positions = exchange.get_positions()
    pnl = exchange.get_pnl()
    print(f'\nPositions after: {positions}')
    print(f'\nPnL after: {pnl:.2f}')


def clear_orders(exchange):
    for id in exchange.get_instruments():
        orders = exchange.get_outstanding_orders(id)
        if len(orders) == 0:
            print(f'-- No limit order in {id}, skipping..')
            continue
        print(f'-- Outstanding limit orders in {id}: ')
        for order, order_status in orders.items():
            print(f'>>>> Deleting limit order on {order_status.side} side, with price {order_status.price} and volume {order_status.volume}.')
        exchange.delete_orders(id)


if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()

    clear_orders(exchange)
    clear_position(exchange)
