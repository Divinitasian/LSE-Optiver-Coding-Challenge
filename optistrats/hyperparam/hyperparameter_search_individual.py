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

project_name = 'Optiver-market-making'


# 🐝 Step 1: Define the trade function that takes in hyperparameter 
# values from `wandb.config` and uses them to maket market on an instrument and return metric
def trade_one_iteration(iteration, market_maker, exchange, underlying_id, wait_time, credit_ic_mode, volume_ic_mode):
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION {iteration} ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')
    
    market_maker.get_traded_orders(exchange)
    
    order_book = exchange.get_last_price_book(instrument_id=underlying_id)
    stock_value = get_bid_ask(order_book)
    if stock_value is None:
        print('Empty stock order book on bid or ask-side, or both, unable to update option prices.')
        time.sleep(wait_time)
        return exchange.get_pnl(), exchange.get_positions()[market_maker.primal.instrument_id]
        

    stock_bid, stock_ask = stock_value
    theoretical_bid_price, theoretical_ask_price = market_maker.compute_fair_quotes(stock_bid.price, stock_ask.price)
    market_maker.select_credits(exchange, credit_ic_mode)
    market_maker.select_volumes(exchange, volume_ic_mode)
    market_maker.cancel_orders(exchange)
    market_maker.update_limit_orders(exchange, theoretical_bid_price, theoretical_ask_price)
    
    print(f'\nSleeping for {wait_time} seconds.')
    time.sleep(wait_time)
    return exchange.get_pnl(), exchange.get_positions()[market_maker.primal.instrument_id]
    
    
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
    # note that we define values from `wandb.config` instead of 
    # defining hard values
    instrument_id = wandb.config.instrument_id
    
    # Create market maker
    if instrument_id[-1] == 'C' or instrument_id[-1] == 'P':
        market_maker = OptionMarketMaker(
            all_instruments[instrument_id],
            wandb.config.credit,
            wandb.config.volume,
            wandb.config.ir,
            wandb.config.vol,
            wandb.config.position_limit,
            wandb.config.tick_size
            )
    elif instrument_id[-1] == 'F':
        market_maker = FutureMarketMaker(
            all_instruments[instrument_id],
            wandb.config.credit,
            wandb.config.volume,
            wandb.config.ir,
            wandb.config.vol,
            wandb.config.position_limit,
            wandb.config.tick_size
            )
    else:
        market_maker = StockMarketMaker(
            all_instruments[instrument_id],
            wandb.config.credit,
            wandb.config.volume,
            wandb.config.ir,
            wandb.config.vol,
            wandb.config.position_limit,
            wandb.config.tick_size
            )
    
    # Initializing
    pnl_0 = exchange.get_pnl()
    epochs = wandb.config.epochs
    
    # Trading
    for epoch in np.arange(1, epochs):
        pnl, pos = trade_one_iteration(
            epoch, 
            market_maker, 
            exchange, 
            wandb.config.underlying_id, 
            wandb.config.wait_time, 
            wandb.config.credit_ic_mode, 
            wandb.config.volume_ic_mode
            )
        wandb.log({
            'PnL': pnl - pnl_0,
            'Position': pos
        })
        
    # Clearing
    clear_orders(exchange)
    clear_position(exchange)
    pnl_1 = exchange.get_pnl()
    tot = pnl_1 - pnl_0
    print(f'\n The cumulative PnL over the trading loop is {tot}.')
    wandb.log({
        'PnL': tot,
        'Position': 0
    })
      
            
# 🐝 Step 2: Define sweep config     
sweep_configuration = {
    'method': 'random',
    'name': 'individual instrument',
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
        # 'credit': {'value': .03},
        'volume': {
            'max': 100, 
            'min': 10
        },
        # 'volume': {'value': 80},
        'credit_ic_mode': {
            'values': [
                'constant', 'rigid', 'linear-advocate', 'slippery'
                ]
        },
        # 'credit_ic_mode': {'value': 'slippery'},
        'volume_ic_mode': {
            'values': [
                'constant', 'linear-advocate', 'linear-deprecate'
                ]
        },
        # 'volume_ic_mode': {'value': 'constant'},
        'instrument_id': {
            'value': 'NVDA_202306_030P'
        },
        'wait_time': {'value': .2},
        'underlying_id': {'value': 'NVDA'},
        'epochs': {'value': 1000},
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