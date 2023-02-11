import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange
from optibook.common_types import InstrumentType, OptionKind

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, check_and_get_best_bid_ask
from libs import round_down_to_tick, round_up_to_tick, clear_orders, clear_position
from libs import POSITION_LIMIT, TICK_SIZE, MAX_BUYING_PRICE, MIN_SELLING_PRICE
from libs import calculate_option_delta, calculate_theoretical_option_value
from libs import INTEREST_RATE, VOLATILITY


logging.getLogger('client').setLevel('ERROR')


class MarketMaker:
    def __init__(self, instrument_id, reference_id):
        self.instrument_id = instrument_id
        self.reference_id = reference_id
        self.bid = None
        self.ask = None
        self.sides = None
        self.reference_prices = None
    
    def set_sides(self, direction):
        """
        Set the target side on which the trader makes market.
        
        Arguments:
            - direction (str): 'long', 'short' or 'both'
        """
        if direction == "long":
            if self.instrument_id[-1] == 'P':
                self.sides = ['ask']
            else:
                self.sides = ['bid']
        elif direction == "short":
            if self.instrument_id[-1] == 'P':
                self.sides = ['bid']
            else:
                self.sides = ['ask']
        else:
            self.sides = ['bid', 'ask']
            
    
    def collect(self, exchange):
        """
        Retrieve from exchange the best quote prices of the reference.
        
        Argument:
            - exchange (optibook.Exchange): an exchange API client
        """
        while True:
            exists, bid, ask = check_and_get_best_bid_ask(
                exchange, 
                self.reference_id
                )
            if exists:
                break
        self.reference_prices = {
            'bid': bid.price,
            'ask': ask.price
        }
        
    