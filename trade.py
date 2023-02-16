import datetime as dt
import time
import logging

from libs import get_bid_ask

logging.getLogger('client').setLevel('ERROR')


from optibook.synchronous_client import Exchange
from optibook.common_types import InstrumentType, OptionKind

from market_maker import OptionMarketMaker, FutureMarketMaker, StockMarketMaker


def underlying_hash(all_instruments):
    underlying_dict = {}
    for instrument_id, instrument in all_instruments.items():
        if instrument.base_instrument_id is not None:
            underlying_dict[instrument_id] = instrument.base_instrument_id
        elif instrument_id[-1] == 'L':
            underlying_dict[instrument_id] = instrument_id.split('_')[0]
        else:
            underlying_dict[instrument_id] = instrument_id
    return underlying_dict
    
    
def market_makers_hash(all_instruments, all_instruments_underlying_ids):
    all_market_makers = {}
    for instrument_id, underlying_id in all_instruments_underlying_ids.items():
        if instrument_id[-1] == 'C' or instrument_id[-1] == 'P':
            market_maker = OptionMarketMaker(all_instruments[instrument_id])
        elif instrument_id[-1] == 'F':
            market_maker = FutureMarketMaker(all_instruments[instrument_id])
        else:
            market_maker = StockMarketMaker(all_instruments[instrument_id])
           
        all_market_makers[instrument_id] = market_maker
    return all_market_makers

if __name__ == "__main__":
    exchange = Exchange()
    exchange.connect()
    
    all_instruments = exchange.get_instruments()
    underlying_dict = underlying_hash(all_instruments)
    market_makers_dict = market_makers_hash(all_instruments, underlying_dict)

    ic_mode = 'linear'
    wait_time = .2
    
    while True:
        print(f'')
        print(f'-----------------------------------------------------------------')
        print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
        print(f'-----------------------------------------------------------------')
        
        for instrument_id, market_maker in market_makers_dict.items():
            market_maker.get_traded_orders(exchange)
        
            stock_value = get_bid_ask(exchange, underlying_dict[instrument_id])
            if stock_value is None:
                print('Empty stock order book on bid or ask-side, or both, unable to update option prices.')
                time.sleep(wait_time)
                continue
        
            stock_bid, stock_ask = stock_value
            theoretical_bid_price, theoretical_ask_price = market_maker.compute_fair_quotes(stock_bid.price, stock_ask.price)
            market_maker.select_credits(exchange, ic_mode)
            market_maker.update_limit_orders(exchange, theoretical_bid_price, theoretical_ask_price)
            
            print(f'\nSleeping for {wait_time} seconds.')
            time.sleep(wait_time)