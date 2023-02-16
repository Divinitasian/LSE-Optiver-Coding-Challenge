import datetime as dt
import time, math
import logging
logging.getLogger('client').setLevel('ERROR')

from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, round_down_to_tick, round_up_to_tick
from libs import get_bid_ask
from libs import INTEREST_RATE, VOLATILITY, POSITION_LIMIT, TICK_SIZE

from optibook.synchronous_client import Exchange
from optibook.common_types import OptionKind


class MarketMaker:
    def __init__(self, instrument):
        self.primal = instrument

        self.interest_rate = INTEREST_RATE
        self.volatility = VOLATILITY
        self.position_limit = POSITION_LIMIT
        self.tick_size = TICK_SIZE
        
        self.credit_bid = 0.03
        self.credit_ask = 0.03

        self.volume_bid = 80
        self.volume_ask = 80
        
        
    def get_traded_orders(self, exchange):
        """
        Print any new trades
        """
        trades = exchange.poll_new_trades(instrument_id=self.primal.instrument_id)
        for trade in trades:
            print(f'- Last period, traded {trade.volume} lots in {self.primal.instrument_id} at price {trade.price:.2f}, side {trade.side}.')


    def update_limit_orders(self, exchange, theoretical_bid_price, theoretical_ask_price):
        """
        This function updates the quotes specified by instrument id. We take the following actions in sequence:
            - pull (remove) any current oustanding orders
            - add credit to theoretical price and round to nearest tick size to create a set of bid/ask quotes
            - calculate max volumes to insert as to not pass the position_limit
            - reinsert limit orders on those levels
    
        Arguments:
            exchange: Exchange           - an exchange client 
            theoretical_bid_price: float   -  Price to bid around
            theoretical_ask_price: float   -  Price to ask around
        """
        # Pull (remove) all existing outstanding orders
        orders = exchange.get_outstanding_orders(instrument_id=self.primal.instrument_id)
        for order_id, order in orders.items():
            print(f'- Deleting old {order.side} order in {self.primal.instrument_id} for {order.volume} @ {order.price:8.2f}.')
            exchange.delete_order(instrument_id=self.primal.instrument_id, order_id=order_id)
    
        # Calculate bid and ask price
        bid_price = round_down_to_tick(theoretical_bid_price - self.credit_bid, self.tick_size)
        ask_price = round_up_to_tick(theoretical_ask_price + self.credit_ask, self.tick_size)
    
        # Calculate bid and ask volumes, taking into account the provided position_limit
        position = exchange.get_positions()[self.primal.instrument_id]
    
        max_volume_to_buy = self.position_limit - position
        max_volume_to_sell = self.position_limit + position
    
        bid_volume = min(self.volume_bid, max_volume_to_buy)
        ask_volume = min(self.volume_ask, max_volume_to_sell)
    
        # Insert new limit orders
        if bid_volume > 0:
            print(f'- Inserting bid limit order in {self.primal.instrument_id} for {bid_volume} @ {bid_price:8.2f}.')
            exchange.insert_order(
                instrument_id=self.primal.instrument_id,
                price=bid_price,
                volume=bid_volume,
                side='bid',
                order_type='limit',
            )
        if ask_volume > 0:
            print(f'- Inserting ask limit order in {self.primal.instrument_id} for {ask_volume} @ {ask_price:8.2f}.')
            exchange.insert_order(
                instrument_id=self.primal.instrument_id,
                price=ask_price,
                volume=ask_volume,
                side='ask',
                order_type='limit',
            )


class StockMarketMaker(MarketMaker):
    def compute_fair_quotes(self, stock_bid_price, stock_ask_price):
        return stock_bid_price, stock_ask_price
        
        
class FutureMarketMaker(MarketMaker):
    def compute_fair_quotes(self, stock_bid_price, stock_ask_price):
        tau = calculate_current_time_to_date(self.primal.expiry)
        ratio = math.exp(self.interest_rate*tau)
        return stock_bid_price * ratio, stock_ask_price * ratio
        

class OptionMarketMaker(MarketMaker):
    def _calculate_theoretical_option_value(self, stock_value):
        """
        This function calculates the current fair call or put value based on Black & Scholes assumptions.
    
        stock_value:             -  Assumed stock value when calculating the Black-Scholes value
        """
        expiry = self.primal.expiry
        strike = self.primal.strike
        option_kind = self.primal.option_kind
        time_to_expiry = calculate_current_time_to_date(expiry)
    
        if option_kind == OptionKind.CALL:
            option_value = call_value(S=stock_value, K=strike, T=time_to_expiry, r=self.interest_rate, sigma=self.volatility)
        elif option_kind == OptionKind.PUT:
            option_value = put_value(S=stock_value, K=strike, T=time_to_expiry, r=self.interest_rate, sigma=self.volatility)
            
        return option_value
        
        
    def compute_fair_quotes(self, stock_bid_price, stock_ask_price):
        theoretical_value_1 = self._calculate_theoretical_option_value(
            stock_bid_price
            )
        theoretical_value_2 = self._calculate_theoretical_option_value(
            stock_ask_price
            )
        theoretical_bid_price = min(theoretical_value_1, theoretical_value_2)
        theoretical_ask_price = max(theoretical_value_1, theoretical_value_2)
        return theoretical_bid_price, theoretical_ask_price
        
        

if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()
    market_maker = FutureMarketMaker(exchange.get_instruments()['NVDA_202309_F'])
    
    wait_time = 1
    
    while True:
        print(f'')
        print(f'-----------------------------------------------------------------')
        print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
        print(f'-----------------------------------------------------------------')
        
        market_maker.get_traded_orders(exchange)
    
        stock_value = get_bid_ask(exchange, 'NVDA')
        if stock_value is None:
            print('Empty stock order book on bid or ask-side, or both, unable to update option prices.')
            time.sleep(wait_time)
            continue
    
        stock_bid, stock_ask = stock_value
        theoretical_bid_price, theoretical_ask_price = market_maker.compute_fair_quotes(stock_bid.price, stock_ask.price)
        market_maker.update_limit_orders(exchange, theoretical_bid_price, theoretical_ask_price)
        
        print(f'\nSleeping for {wait_time} seconds.')
        time.sleep(wait_time)





