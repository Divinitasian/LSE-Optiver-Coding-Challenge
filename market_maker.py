import libs
import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange

logging.getLogger('client').setLevel('ERROR')


def _make_market_profitable(theoretical_price, best_quote, side, tick_size, credit):
    if side == 'bid':
        if best_quote is None:
            price = theoretical_price + credit
            volume = libs.POSITION_LIMIT * 2
            profitable = True
        else:
            price = best_quote.price + tick_size
            volume = best_quote.volume
            profitable = theoretical_price > price
    else:
        if best_quote is None:
            price = theoretical_price - credit
            volume = libs.POSITION_LIMIT * 2
            profitable = True        
        else:
            price = best_quote.price - tick_size
            volume = best_quote.volume
            profitable = theoretical_price < price
    return profitable, price, volume
    
    
def _detect(best_quote_price, theoretical_price, credit, side):
    buy_side_arbitragable = (side == 'bid') and (best_quote_price > theoretical_price)
    sell_side_arbitragable = (side == 'ask') and (best_quote_price < theoretical_price)
    buy_side_marketmakable = (side == 'bid') and (best_quote_price + libs.TICK_SIZE <= theoretical_price - credit)
    sell_side_marketmakable = (side == 'ask') and (best_quote_price - libs.TICK_SIZE >= theoretical_price + credit)
    if buy_side_arbitragable or sell_side_arbitragable:
        return 'take'
    elif buy_side_marketmakable or sell_side_marketmakable:
        return 'make'
    else:
        return 'skip'
    

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
    
    def make_market(self, exchange, default_credit=0.03):
        """
        Provide liquidity to the current order book when it is profitable.
        """
        exchange.delete_orders(self.instrument_id)
        order_book = exchange.get_last_price_book(self.instrument_id)
        for side in self.sides:
            best_quote = libs.get_best_quote(order_book, side)
            profitable, price, volume = _make_market_profitable(
                self.theoretical_prices[side],
                best_quote,
                side,
                libs.TICK_SIZE,
                default_credit
                )
            if profitable:
                position = exchange.get_positions()[self.instrument_id]
                volume = libs.get_valid_volume(
                    volume,
                    position,
                    self.max_volume, 
                    side
                    )
                if volume > 0:
                    print(f'- Inserting {side} limit order in {self.instrument_id} for {volume} @ {price:8.2f}.')
                    exchange.insert_order(
                        instrument_id=self.instrument_id,
                        price=price,
                        volume=volume,
                        side=side,
                        order_type='limit',
                    )


        
            
        
    