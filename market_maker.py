import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange
from optibook.common_types import InstrumentType, OptionKind

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, retrieve_best_quotes
from libs import round_down_to_tick, round_up_to_tick, clear_orders, clear_position
from libs import POSITION_LIMIT, TICK_SIZE, MAX_BUYING_PRICE, MIN_SELLING_PRICE
from libs import calculate_option_delta, calculate_theoretical_option_value
from libs import INTEREST_RATE, VOLATILITY


logging.getLogger('client').setLevel('ERROR')


class MarketMaker:
    def __init__(self, instrument_id, reference_id, max_volume=80):
        self.instrument_id = instrument_id
        self.reference_id = reference_id
        self.sides = None
        self.reference_prices = None
        self.theoretical_prices = None
        self.max_volume = max_volume
    
    def set_sides(self, direction):
        """
        Set the target side on which the trader makes market.
        
        Arguments:
            - direction (str): 'long', 'short' or 'both'
        """
        if direction == "long":
            self.sides = ['bid']
        elif direction == "short":
            self.sides = ['ask']
        else:
            self.sides = ['bid', 'ask']
            
    
    def collect(self, exchange):
        """
        Retrieve from exchange the best quote prices of the reference.
        
        Argument:
            - exchange (optibook.Exchange): an exchange API client
        """
        bid, ask = retrieve_best_quotes(exchange, self.reference_id)
        self.reference_prices = {
            'bid': bid.price,
            'ask': ask.price
        }
        
    
    def price(self):
        """
        Compute the theoretical prices of the instrument on both sides.
        """
        self.theoretical_prices = {
            'bid': self.reference_prices['bid'],
            'ask': self.reference_prices['ask']
        }
        
    
    # def make_market(self, exchange):
    #     """
    #     Provide or take liquidity from the current order book.
    #     """
    #     exchange.delete_orders(self.instrument_id)
        
        
        
            
        
    