import random
import numpy as np
import datetime as dt
import time, math
import logging
logging.getLogger('client').setLevel('ERROR')

from optibook.synchronous_client import Exchange
from market_maker import OptionMarketMaker, FutureMarketMaker, StockMarketMaker
from libs import get_bid_ask


# 🐝 Step 1: Define the trade function that takes in hyperparameter 
# values from `wandb.config` and uses them to maket market on an instrument and return metric
def trade_one_iteration(iteration, market_maker, exchange, underlying_id, wait_time, credit_ic_mode, volume_ic_mode):
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION {iteration} ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')
    
    market_maker.get_traded_orders(exchange)
    
    stock_value = get_bid_ask(exchange, underlying_id)
    if stock_value is None:
        print('Empty stock order book on bid or ask-side, or both, unable to update option prices.')
        time.sleep(wait_time)
        return exchange.get_pnl()
        

    stock_bid, stock_ask = stock_value
    theoretical_bid_price, theoretical_ask_price = market_maker.compute_fair_quotes(stock_bid.price, stock_ask.price)
    market_maker.select_credits(exchange, credit_ic_mode)
    market_maker.select_volumes(exchange, volume_ic_mode)
    market_maker.cancel_orders(exchange)
    market_maker.update_limit_orders(exchange, theoretical_bid_price, theoretical_ask_price)
    
    print(f'\nSleeping for {wait_time} seconds.')
    time.sleep(wait_time)
    return exchange.get_pnl()