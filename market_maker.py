import libs
import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange

logging.getLogger('client').setLevel('ERROR')


class MarketMaker:
    def __init__(self, instrument_id, reference_id, max_volume=80):
        self.instrument_id = instrument_id
        self.reference_id = reference_id
        self.sides = None
        self.reference = {
            'bid': None, 'ask': None
        }
        self.theoretical_prices = {
            'bid': None, 'ask': None
        }
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
        bid, ask = libs.retrieve_best_quotes(exchange, self.reference_id)
        self.reference['bid'] = bid
        self.reference['ask'] = ask
        
    
    def price(self):
        """
        Compute the theoretical prices of the instrument on both sides.
        """
        self.theoretical_prices['bid'] = self.reference['bid'].price 
        self.theoretical_prices['ask'] = self.reference['ask'].price
    
    
    # def make_market(self, exchange):
    #     """
    #     Provide liquidity to the current order book when it is profitable.
    #     """
    #     exchange.delete_orders(self.instrument_id)
        
        
        
        
            
        
    