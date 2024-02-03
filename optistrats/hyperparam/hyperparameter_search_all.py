import random
import numpy as np
import datetime as dt
import time, math
import logging
logging.getLogger('client').setLevel('ERROR')

import wandb
wandb.login()

from optibook.synchronous_client import Exchange
from optistrats.strats.market_maker import OptionMarketMaker, FutureMarketMaker, StockMarketMaker
from optistrats.utils import get_bid_ask, clear_orders, clear_position
from optistrats.scripts.run import underlying_hash, market_makers_hash

project_name = 'Optiver-market-making'


# 🐝 Step 1: Define the trade function that takes in hyperparameter 
# values from `wandb.config` and uses them to maket market on an instrument and return metric
def trade_one_iteration(iteration, market_makers_dict, underlying_dict, exchange, wait_time, credit_ic_mode, volume_ic_mode):
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION {iteration} ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')
    
    for instrument_id, market_maker in market_makers_dict.items():
        market_maker.get_traded_orders(exchange)
        
        stock_value = get_bid_ask(exchange, underlying_dict[instrument_id])
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
    
    
def main():
    # Use the wandb.init() API to generate a background process 
    # to sync and log data as a Weights and Biases run.
    # Optionally provide the name of the project. 
    run = wandb.init(project=project_name)
    exchange = Exchange()
    exchange.connect()
    # clear all orders
    clear_orders(exchange)
    clear_position(exchange)
    
    all_instruments = exchange.get_instruments()
    underlying_dict = underlying_hash(all_instruments)
    market_makers_dict = market_makers_hash(all_instruments, underlying_dict)
    # note that we define values from `wandb.config` instead of 
    # defining hard values
    
    # Initializing
    pnl_0 = exchange.get_pnl()
    epochs = wandb.config.epochs
    
    # Trading
    for epoch in np.arange(1, epochs):
        pnl = trade_one_iteration(
            epoch, 
            market_makers_dict,
            underlying_dict,
            exchange, 
            wandb.config.wait_time, 
            wandb.config.credit_ic_mode, 
            wandb.config.volume_ic_mode
            )
        wandb.log({
            'PnL': pnl - pnl_0
        })
        
    # Clearing
    clear_orders(exchange)
    clear_position(exchange)
    pnl_1 = exchange.get_pnl()
    tot = pnl_1 - pnl_0
    print(f'\n The cumulative PnL over the trading loop is {tot}.')
    wandb.log({
        'PnL': tot
    })
      
            
# 🐝 Step 2: Define sweep config     
sweep_configuration = {
    'method': 'random',
    'name': 'all instruments',
    'metric': {
        'goal': 'maximize',
        'name': 'PnL'
    },
    'early_terminate': {
        'type': 'hyperband',
        'min_iter': 3
    },
    'parameters': {
        'credit': {
            'max': 0.1, 
            'min': 0.01
        },
        'volume': {
            'max': 100, 
            'min': 10
        },
        'credit_ic_mode': {
            'values': [
                'constant', 'rigid', 'linear-advocate'
                ]
        },
        'volume_ic_mode': {
            'values': [
                'constant', 'linear-advocate', 'linear-deprecate'
                ]
        },
        'wait_time': {'value': .2},
        'epochs': {'value': 100},
        'ir': {'value': .03},
        'vol': {'value': 3},
        'position_limit': {'value': 100},
        'tick_size': {'value': .1}
    }
}



# 🐝 Step 3: Initialize sweep by passing in config
sweep_id = wandb.sweep(sweep=sweep_configuration, project=project_name)

# 🐝 Step 4: Call to `wandb.agent` to start a sweep
wandb.agent(sweep_id, function=main, count=100)