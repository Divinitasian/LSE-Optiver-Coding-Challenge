from optibook.synchronous_client import Exchange
import logging
from optistrats.utils import clear_orders, clear_position

if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()

    logging.getLogger('client').setLevel('ERROR')
    clear_orders(exchange)
    clear_position(exchange)