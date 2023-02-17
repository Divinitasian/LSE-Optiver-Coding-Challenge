import datetime as dt
import time, math
import logging
logging.getLogger('client').setLevel('ERROR')

from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, round_down_to_tick, round_up_to_tick
from libs import get_bid_ask

from optibook.synchronous_client import Exchange
from optibook.common_types import OptionKind


class MarketMaker:
    def __init__(self, instrument, credit=0.03, volume=80, credit_max=0.1, ir=.03, vol=3, position_limit=100, tick_size=0.1):
        self.primal = instrument
        # trading environment and exchange resolution parameters
        self.interest_rate = ir
        self.volatility = vol
        self.position_limit = position_limit
        self.tick_size = tick_size
        # market making algorithm hyperparameters
        self.c0 = credit
        self.v0 = volume
        self.cmax = credit_max
        
    def get_traded_orders(self, exchange):
        """
        Print any new trades
        """
        trades = exchange.poll_new_trades(instrument_id=self.primal.instrument_id)
        for trade in trades:
            print(f'- Last period, traded {trade.volume} lots in {self.primal.instrument_id} at price {trade.price:.2f}, side {trade.side}.')
            
            
    def cancel_orders(self, exchange):
        """
        Remove any current oustanding orders
        """
        orders = exchange.get_outstanding_orders(instrument_id=self.primal.instrument_id)
        for order_id, order in orders.items():
            print(f'- Deleting old {order.side} order in {self.primal.instrument_id} for {order.volume} @ {order.price:8.2f}.')
            exchange.delete_order(instrument_id=self.primal.instrument_id, order_id=order_id)
    

    def update_limit_orders(self, exchange, theoretical_bid_price, theoretical_ask_price):
        """
        This function updates the quotes specified by instrument id. We take the following actions in sequence:
            - add credit to theoretical price and round to nearest tick size to create a set of bid/ask quotes
            - calculate max volumes to insert as to not pass the position_limit
            - reinsert limit orders on those levels
    
        Arguments:
            exchange: Exchange           - an exchange client 
            theoretical_bid_price: float   -  Price to bid around
            theoretical_ask_price: float   -  Price to ask around
        """
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
            
    
    def _volume_constant(self):
        self.volume_bid = self.v0
        self.volume_ask = self.v0        
        
        
    def _volume_linear_deprecate(self, exchange):
        self.volume_bid = self.v0
        self.volume_ask = self.v0            
        instrument_id = self.primal.instrument_id
        position = exchange.get_positions()[instrument_id]
        factor = 1 - abs(position) / self.position_limit
        if position > 0:
            self.volume_bid = int(self.volume_bid * factor)
        elif position < 0:
            self.volume_ask = int(self.volume_ask * factor)
            
    
    def _volume_linear_advocate(self, exchange):
        self.volume_bid = self.v0
        self.volume_ask = self.v0            
        instrument_id = self.primal.instrument_id
        position = exchange.get_positions()[instrument_id]
        factor = 1 - abs(position) / self.position_limit
        v = int(self.v0 * factor + abs(position))
        if position > 0:
            self.volume_ask = v
        elif position < 0:
            self.volume_bid = v
        
    
    def select_volumes(self, exchange, ic_mode):
        if ic_mode == 'constant':
            self._volume_constant()
        elif ic_mode == 'linear-deprecate':
            self._volume_linear_deprecate(exchange)
        elif ic_mode == 'linear-advocate':
            self._volume_linear_advocate(exchange)
        else:
            raise NotImplementedError(f"The volume {ic_mode} mode for inventory management has not been implemented.")
                
                
    def _credit_constant(self):
        self.credit_bid = self.c0
        self.credit_ask = self.c0   
        
                
    def _credit_linear_advocate(self, exchange):
        self.credit_bid = self.c0
        self.credit_ask = self.c0
        instrument_id = self.primal.instrument_id
        position = exchange.get_positions()[instrument_id]
        factor = 1 - abs(position) / self.position_limit
        if position > 0:
            self.credit_ask *= factor
        elif position < 0:
            self.credit_bid *= factor
            
                
    def _credit_rigid(self, exchange):
        self.credit_bid = self.c0
        self.credit_ask = self.c0
        instrument_id = self.primal.instrument_id
        position = exchange.get_positions()[instrument_id]
        if position == self.position_limit:
            self.credit_ask = 0
        elif position == -self.position_limit:
            self.credit_bid = 0        
    
                
    def select_credits(self, exchange, ic_mode):
        if ic_mode == 'constant':
            self._credit_constant()
        elif ic_mode == 'rigid':
            self._credit_rigid(exchange)
        elif ic_mode == 'linear-advocate':
            self._credit_linear_advocate(exchange)
        else:
            raise NotImplementedError(f"The credit {ic_mode} mode for inventory management has not been implemented.")
                

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
    market_maker = OptionMarketMaker(exchange.get_instruments()['NVDA_202306_050P'])
    
    credit_ic_mode = 'linear-advocate'
    volume_ic_mode = 'linear-advocate'
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
        market_maker.select_credits(exchange, credit_ic_mode)
        market_maker.select_volumes(exchange, volume_ic_mode)
        market_maker.cancel_orders(exchange)
        market_maker.update_limit_orders(exchange, theoretical_bid_price, theoretical_ask_price)
        
        print(f'\nSleeping for {wait_time} seconds.')
        time.sleep(wait_time)





