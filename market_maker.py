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
    def __init__(self, instrument_id, hedge_id):
        self.primal_id = instrument_id
        self.dual_id = hedge_id
    
    def check(self, exchange):
        dual_order_book = exchange.get_last_price_book(self.dual_id)
        return (dual_order_book and dual_order_book.bids and dual_order_book.asks)
            
    def update(self, exchange, theoretical_bidprice, theoretical_askprice, credit, volume):
        """
        This function updates the quotes for <instrument_id> in the following steps:
        
            - pull (remove) any current outstanding orders
            - add credit to theoretical price and round to nearest tick size to create a set of quotes
            - calculate the max volume to insert as to not pass the position_limit
            - reinsert limit orders on those levels
            
        Argument:
            exchange: Exchange()                 -  the stock exchange client
            theoretical_bidprice: float          -  the theoretical bid price to quote around
            theoretical_askprice: float          -  the theoretical ask price to quote around
            credit: float                        -  Difference to subtract from/add to theoretical price to come to final bid/ask price
            volume: int                          -  Volume (# lots) of the inserted orders (given they do not breach position limits)
        """
        print(f"\nUpdating instrument {self.primal_id}")
        # Print any new trades
        trades = exchange.poll_new_trades(instrument_id=self.primal_id)
        for trade in trades:
            print(f'- Last period, traded {trade.volume} lots in {self.primal_id} at price {trade.price:.2f}, side {trade.side}.')
    
        # Pull (remove) all existing outstanding orders
        orders = exchange.get_outstanding_orders(instrument_id=self.primal_id)
        for order_id, order in orders.items():
            print(f'- Deleting old {order.side} order in {self.primal_id} for {order.volume} @ {order.price:.2f}.')
            exchange.delete_order(instrument_id=self.primal_id, order_id=order_id)
            
        # Calculate bid and ask price
        bid_price = round_down_to_tick(theoretical_bidprice - credit, TICK_SIZE)
        ask_price = round_up_to_tick(theoretical_askprice + credit, TICK_SIZE)
        
        # Calculate bid and ask volumes, taking into account the provided position_limit
        position = exchange.get_positions()[self.primal_id]

        max_volume_to_buy = POSITION_LIMIT - position
        max_volume_to_sell = POSITION_LIMIT + position
    
        bid_volume = min(volume, max_volume_to_buy)
        ask_volume = min(volume, max_volume_to_sell)
        
        # Insert new limit orders
        if bid_volume > 0:
            print(f'- Inserting bid limit order in {self.primal_id} for {bid_volume} @ {bid_price:.2f}.')
            exchange.insert_order(
                instrument_id=self.primal_id,
                price=bid_price,
                volume=bid_volume,
                side='bid',
                order_type='limit',
            )
        if ask_volume > 0:
            print(f'- Inserting ask limit order in {self.primal_id} for {ask_volume} @ {ask_price:.2f}.')
            exchange.insert_order(
                instrument_id=self.primal_id,
                price=ask_price,
                volume=ask_volume,
                side='ask',
                order_type='limit',
            )
        
            
    def hedge(self, exchange, delta):
        """
        This function hedges the outstanding position in illiquid order book specified by <instrument_id> using liquid asset specified by <hedge_id>.
    
        That is:
            - It calculates how sensitive the total position value is to changes in the underlying by summing up all
              individual delta component.
            - And then trades liquid assets which have the opposite exposure, to remain, roughly, flat delta exposure
            
                
        Argument:
            exchange: Exchange()                 -  the stock exchange client
            delta: float                         -  sensitivity of the portfolio price to the dual asset
        """
        print(f'\nHedging delta position')
        positions = exchange.get_positions()
        # Trade in the dual asset order book, staying mindful of the overall position-limit of 100.
        desired_dual_position = max(min(-delta, POSITION_LIMIT), -POSITION_LIMIT) 
        current_dual_position = positions[self.dual_id]
        print(f'The current position in {self.dual_id} is {current_dual_position}.')
        diff = desired_dual_position - current_dual_position
        if diff >= 1 :
            side, price = 'bid', MAX_BUYING_PRICE
            volume = diff
        elif diff <= -1:
            side, price = 'ask', MIN_SELLING_PRICE
            volume = -diff
        else:
            print(f'\n- Skipping...')
            return
        volume = int(volume)
        print(f'\n- Inserting {side} market order in {self.dual_id} for {volume} @ {price:.2f}.')
        exchange.insert_order(
                instrument_id=self.dual_id,
                price=price,
                volume=volume,
                side=side,
                order_type='ioc',            
            )
            

class LinearDerivativeMarketMaker(MarketMaker):
    def get_fair_prices(self, exchange):
        dual_order_book = exchange.get_last_price_book(self.dual_id)
        return dual_order_book.bids[0].price, dual_order_book.asks[0].price
        
    def compute_delta(self, exchange):
        """
        This function calculates how sensitive the marketmaker's position in the primal instrument that is linear in the dual instrument.
            
                
        Argument:
            exchange: Exchange()                 -  the stock exchange client
        """
        # Calculate the delta position here
        positions = exchange.get_positions()
        primal_position = positions[self.primal_id]
        print(f"The current position in {self.primal_id} is {primal_position}.")
        delta = primal_position
        return delta


class OptionMarketMaker(MarketMaker):
    """
    Primal: option
    Dual: stock
    """
    def get_fair_prices(self, exchange):
        """
        This function calculate the fair bid/ask for the option using BS formula
        
            - get bid/ask from the stock
            - get the features of the option
            - plug into the BS formula
        
        Argument:
            exchange: Exchange()                 -  the stock exchange client
        """        
        # stock and option information
        stock_order_book = exchange.get_last_price_book(self.dual_id)
        option = exchange.get_instruments()[self.primal_id]
        # BS formula for bid/ask price
        price = lambda stock_value: calculate_theoretical_option_value(
            option.expiry, 
            option.strike, 
            option.option_kind, 
            stock_value, 
            INTEREST_RATE, 
            VOLATILITY
            )
        return price(stock_order_book.bids[0].price), price(stock_order_book.asks[0].price)
        
        
    def compute_delta(self, exchange):
        """
        This function calculates how sensitive the marketmaker's position in option to the stock price
        
            - get position of the options
            - compute the stock value
            - plug into the BS formula
        
        Argument:
            exchange: Exchange()                 -  the stock exchange client
        """
        # get the position in the option
        position = exchange.get_positions()[self.primal_id]
        print(f"The current position in {self.primal_id} is {position}.")
        if position == 0:
            return 0
        
        # specify the stock value used in computing delta
        option = exchange.get_instruments()[self.primal_id]
        option_order_book = exchange.get_last_price_book(self.dual_id)
        bid_price = option_order_book.bids[0].price
        ask_price = option_order_book.asks[0].price
        option_kind = option.option_kind
        if ((option_kind == OptionKind.CALL) and (position > 0)) or ((option_kind == OptionKind.PUT) and (position < 0)):
            stock_value = bid_price
        else:
            stock_value = ask_price
        
        # compute the delta using BS formula
        delta = position * calculate_option_delta(
                            option.expiry, 
                            option.strike, 
                            option_kind, 
                            stock_value, 
                            INTEREST_RATE, 
                            VOLATILITY
                            )
        return delta


if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()
    
    clear_position(exchange)
    clear_orders(exchange)
    
    instrument_id, hedge_id = 'NVDA_202306_020C', 'NVDA'
    market_maker = OptionMarketMaker(instrument_id, hedge_id)

    # instrument_id, hedge_id = 'NVDA_DUAL', 'NVDA'
    # market_maker = LinearDerivativeMarketMaker(instrument_id, hedge_id)
    
    while True:
        print(f'')
        print(f'-----------------------------------------------------------------')
        print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
        print(f'-----------------------------------------------------------------')
        
        dual_exists = market_maker.check(exchange)
        if not dual_exists:
            continue
        bid_price, ask_price = market_maker.get_fair_prices(exchange)
        
        credit = .05
        volume = 50

        market_maker.update(
            exchange, 
            bid_price, 
            ask_price, 
            credit, 
            volume
            )
        delta = market_maker.compute_delta(exchange)
        market_maker.hedge(
            exchange,
            delta
            )
        
        rest = 1
        print(f'\nSleeping for {rest} seconds.')
        time.sleep(rest)