import datetime as dt
import time
import random
import math
import logging
from optibook.synchronous_client import Exchange
from optibook.common_types import OptionKind
from math import floor, ceil
from optistrats.math.black_scholes import call_value, put_value, call_delta, put_delta

MIN_SELLING_PRICE = 0.10
MAX_BUYING_PRICE = 100000.00
INTEREST_RATE = .03
VOLATILITY = 3
POSITION_LIMIT = 100
TICK_SIZE = 0.10


option_ids = [
    'NVDA_202306_020C',
    'NVDA_202306_020P',
    'NVDA_202306_030C',
    'NVDA_202306_030P',
    'NVDA_202306_040C',
    'NVDA_202306_040P',
    'NVDA_202306_050C',
    'NVDA_202306_050P',
    ]
future_ids = [
    'NVDA_202306_F',
    'NVDA_202309_F',
    'NVDA_202312_F'
    ]
stock_ids = [
    'NVDA_DUAL'
    ]

def calculate_current_time_to_date(expiry_date) -> float:
    """
    Returns the current total time remaining until some future datetime. The remaining time is provided in fractions of
    years.

    Example usage:
        import datetime as dt

        expiry_date = dt.datetime(2022, 12, 31, 12, 0, 0)
        tte = calculate_current_time_to_date(expiry_date)

    Arguments:
        expiry_date: A dt.datetime object representing the datetime of expiry.
    """
    now = dt.datetime.now()
    return calculate_time_to_date(expiry_date, now)


def calculate_time_to_date(expiry_date, current_time) -> float:
    """
    Returns the total time remaining until some future datetime. The remaining time is provided in fractions of years.

    Example usage:
        import datetime as dt

        expiry_date = dt.datetime(2022, 12, 31, 12, 0, 0)
        now = dt.datetime.now()
        tte = calculate_time_to_date(expiry_date, now)

    Arguments:
        expiry_date: A dt.datetime object representing the datetime of expiry.
        current_time: A dt.datetime object representing the current datetime to assume.
    """

    return (expiry_date - current_time) / dt.timedelta(days=1) / 365
    

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


def trade_would_breach_position_limit(exchange, instrument_id, volume, side, position_limit=100):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]

    if side == 'bid':
        return position_instrument + volume > position_limit
    elif side == 'ask':
        return position_instrument - volume < -position_limit
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')


def print_positions_and_pnl(exchange, always_display=None):
    positions = exchange.get_positions()
    print('Positions:')
    for instrument_id in positions:
        if not always_display or instrument_id in always_display or positions[instrument_id] != 0:
            print(f'  {instrument_id:20s}: {positions[instrument_id]:4.0f}')

    pnl = exchange.get_pnl()
    if pnl:
        print(f'\nPnL: {pnl:.2f}')


def check_and_get_best_bid_ask(exchange, stock_id):
    stock_order_book = exchange.get_last_price_book(stock_id)
    if not (stock_order_book and stock_order_book.bids and stock_order_book.asks): 
        return False, None, None
    else:
        return True, stock_order_book.bids[0], stock_order_book.asks[0]
        
def retrieve_best_quotes(exchange, instrument_id):
    while True:
        exists, bid, ask = check_and_get_best_bid_ask(exchange, instrument_id)
        if exists:
            return bid, ask


def expiry_in_years(exchange, instrument_id):
    '''
    expiry measured in years
    '''
    future_inst = exchange.get_instruments()[instrument_id]
    expiry_date = future_inst.expiry
    return calculate_current_time_to_date(expiry_date)    


def get_pair_option(option_id):
    pair_option_id = option_id[:-1]
    if option_id[-1] == 'C':
        return pair_option_id + 'P'
    else:
        return pair_option_id + 'C'


def get_bid_ask(exchange, instrument_id):
    """
    This function calculates the current midpoint of the order book supplied by the exchange for the instrument
    specified by <instrument_id>, returning None if either side or both sides do not have any orders available.
    """
    order_book = exchange.get_last_price_book(instrument_id=instrument_id)

    # If the instrument doesn't have prices at all or on either side, we cannot calculate a midpoint and return None
    if not (order_book and order_book.bids and order_book.asks):
        return None
    else:
        return order_book.bids[0], order_book.asks[0]


def round_down_to_tick(price, tick_size):
    """
    Rounds a price down to the nearest tick, e.g. if the tick size is 0.10, a price of 0.97 will get rounded to 0.90.
    """
    return floor(price / tick_size) * tick_size


def round_up_to_tick(price, tick_size):
    """
    Rounds a price up to the nearest tick, e.g. if the tick size is 0.10, a price of 1.34 will get rounded to 1.40.
    """
    return ceil(price / tick_size) * tick_size


def get_midpoint_value(exchange, instrument_id):
    """
    This function calculates the current midpoint of the order book supplied by the exchange for the instrument
    specified by <instrument_id>, returning None if either side or both sides do not have any orders available.
    """
    order_book = exchange.get_last_price_book(instrument_id=instrument_id)

    # If the instrument doesn't have prices at all or on either side, we cannot calculate a midpoint and return None
    if not (order_book and order_book.bids and order_book.asks):
        return None
    else:
        midpoint = (order_book.bids[0].price + order_book.asks[0].price) / 2.0
        return midpoint


def calculate_theoretical_option_value(expiry, strike, option_kind, stock_value, interest_rate, volatility):
    """
    This function calculates the current fair call or put value based on Black & Scholes assumptions.

    expiry: dt.date          -  Expiry date of the option
    strike: float            -  Strike price of the option
    option_kind: OptionKind  -  Type of the option
    stock_value:             -  Assumed stock value when calculating the Black-Scholes value
    interest_rate:           -  Assumed interest rate when calculating the Black-Scholes value
    volatility:              -  Assumed volatility of when calculating the Black-Scholes value
    """
    time_to_expiry = calculate_current_time_to_date(expiry)

    if option_kind == OptionKind.CALL:
        option_value = call_value(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)
    elif option_kind == OptionKind.PUT:
        option_value = put_value(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)

    return option_value


def calculate_option_delta(expiry_date, strike, option_kind, stock_value, interest_rate, volatility):
    """
    This function calculates the current option delta based on Black & Scholes assumptions.

    expiry_date: dt.date     -  Expiry date of the option
    strike: float            -  Strike price of the option
    option_kind: OptionKind  -  Type of the option
    stock_value:             -  Assumed stock value when calculating the Black-Scholes value
    interest_rate:           -  Assumed interest rate when calculating the Black-Scholes value
    volatility:              -  Assumed volatility of when calculating the Black-Scholes value
    """
    time_to_expiry = calculate_current_time_to_date(expiry_date)

    if option_kind == OptionKind.CALL:
        option_delta = call_delta(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)
    elif option_kind == OptionKind.PUT:
        option_delta = put_delta(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)
    else:
        raise Exception(f"""Got unexpected value for option_kind argument, should be OptionKind.CALL or OptionKind.PUT but was {option_kind}.""")

    return option_delta
    
    
def show(response):
    if response.success:
        print(f'>> Status: SUCCEED. Order ID: {response.order_id}.')
    else:
        print(f'>> Status: FAILURE. Reason: {response.error_reason}.')
        

def get_quotes(order_book, side):
    if side == 'bid':
        quotes = order_book.bids if order_book else None
    else:
        quotes = order_book.asks if order_book else None
    return quotes
    
def get_best_quote(order_book, side):
    quotes = get_quotes(order_book, side)
    return quotes[0] if quotes else None
        

def get_valid_volume(volume, position, position_limit, side):
    if side == 'bid':
        max_volume_to_buy = position_limit - position
        return min(volume, max_volume_to_buy)
    else: 
        max_volume_to_sell = position_limit + position
        return min(volume, max_volume_to_sell)
        
        
def detect_arbitrage(best_bid_price, best_ask_price, theoretical_bid_price, theoretical_ask_price):
    if best_bid_price > theoretical_ask_price:
        primal_side = "ask"
    elif best_ask_price < theoretical_bid_price:
        primal_side = "bid"
    else:
        primal_side = None
    return primal_side
    
    
def exponential_credit(cmin, cmax, pmax, pmin, position_size):
    k = (math.log(cmax) - math.log(cmin)) / (pmax - pmin)
    b = math.log(cmin) - k * pmin
    return math.exp(k * position_size + b)


def linear_credit(cmin, cmax, pmax, pmin, position_size):
    k = (cmax - cmin) / (pmax - pmin)
    b = cmin - k * pmin
    return k * position_size + b
                
                
def slippery_credit(side, position, c0, cmax, p_threshold, p_limit):
    if side == 'ask':
        position = - position
    if position < - p_threshold:
        return 0
    elif position < 0:
        return linear_credit(0, c0, 0, -p_threshold, position)
    elif position < p_threshold:
        return c0
    elif position <= p_limit:
        return exponential_credit(c0, cmax, p_limit, p_threshold, position)
        
                    
if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()

    logging.getLogger('client').setLevel('ERROR')
    clear_orders(exchange)
    clear_position(exchange)