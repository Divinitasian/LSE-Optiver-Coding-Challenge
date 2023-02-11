import math
import logging
import datetime as dt
import time
from libs import calculate_current_time_to_date, expiry_in_years
from libs import clear_position, print_positions_and_pnl
from libs import trade_would_breach_position_limit, check_and_get_best_bid_ask
from optibook.synchronous_client import Exchange
from optibook.common_types import InstrumentType


INTEREST_RATE = .03
VOLATILITY = 3

exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')


class Arbitrageur:
    def __init__(self, primal_instrument_id, hedge_instrument_id):
        '''
        Primal instrument: illiquid instrument
        Hedge instrument: liquid instrument
        '''
        self.primal_id = primal_instrument_id
        self.hedge_id = hedge_instrument_id
        self.bid_primal = None
        self.ask_primal = None
        self.bid_hedge = None
        self.ask_hedge = None
        self.primal_side = []
    
    def get_best_quotes(self):
        primal_exists, self.bid_primal, self.ask_primal = check_and_get_best_bid_ask(exchange, self.primal_id)
        dual_exists, self.bid_hedge, self.ask_hedge = check_and_get_best_bid_ask(exchange, self.hedge_id)
        return primal_exists and dual_exists
        
    def trade(self):
        for side in self.primal_side:
            # arbitrage operations
            if side == 'bid':
                opposite = 'ask'
                primal_price = self.ask_primal.price
                hedge_price = self.bid_hedge.price
                desiredVolume = min(self.ask_primal.volume, self.bid_hedge.volume)
            else:
                opposite = 'bid'
                primal_price = self.bid_primal.price
                hedge_price = self.ask_hedge.price
                desiredVolume = min(self.bid_primal.volume, self.ask_hedge.volume)
            # trade on primal book
            if not trade_would_breach_position_limit(exchange, self.primal_id, desiredVolume, side):
                print(f'- Inserting {side} ioc order in {self.primal_id} for {desiredVolume} @ {primal_price:8.2f}.')
                response = exchange.insert_order(
                    instrument_id=self.primal_id,
                    price=primal_price,
                    volume=desiredVolume,
                    side=side,
                    order_type='ioc'
                    )
                if response.success:
                    # trade on hedge book
                    tradedVolume = exchange.get_trade_history(self.primal_id)[-1].volume
                    if not trade_would_breach_position_limit(exchange, self.hedge_id, tradedVolume, opposite):
                        print(f'- Inserting {opposite} ioc order in {self.hedge_id} for {tradedVolume} @ {hedge_price:8.2f}.')
                        exchange.insert_order(
                            instrument_id=self.hedge_id,
                            price=hedge_price,
                            volume=tradedVolume,
                            side=opposite,
                            order_type='ioc'
                            )
                            
    def reset(self):
        self.bid_primal = None
        self.ask_primal = None
        self.bid_hedge = None
        self.ask_hedge = None
        self.primal_side = []


class DualListArb(Arbitrageur):
    def detect(self):
        if self.ask_primal.price < self.bid_hedge.price:
            self.primal_side.append('bid')
        if self.bid_primal.price > self.ask_hedge.price:
            self.primal_side.append('ask')
    

class FutureSpotArb(Arbitrageur):
    '''
    Primal instrument: future contract
    Hedge instrument: spot equity
    '''
    def __init__(self, future_id, spot_id):
        super(FutureSpotArb, self).__init__(future_id, spot_id)
        expiry = expiry_in_years(exchange, future_id)
        self.cost_factor = math.exp(INTEREST_RATE * expiry)
        
    def detect(self):
        if self.ask_primal.price < self.bid_hedge.price * self.cost_factor:
            self.primal_side.append('bid')
        if self.bid_primal.price > self.ask_hedge.price * self.cost_factor:
            self.primal_side.append('ask')


###########################
# Trading - Start here #
###########################

if False: 
    clear_position(exchange)


stocks = [
    DualListArb('NVDA_DUAL', 'NVDA'),
    DualListArb('SAN_DUAL', 'SAN'),
    ]
    
futures = []
for id, instrument in exchange.get_instruments().items():
    if instrument.instrument_type == InstrumentType.STOCK_FUTURE:
        futures.append(
            FutureSpotArb(id, instrument.base_instrument_id)
            )

arbitrageurs = stocks + futures

while True:
    print(f'')
    print(f'-----------------------------------------------------------------')
    print(f'TRADE LOOP ITERATION ENTERED AT {str(dt.datetime.now()):18s} UTC.')
    print(f'-----------------------------------------------------------------')
    for arb in arbitrageurs:
        if arb.get_best_quotes():
            arb.detect()
            arb.trade()
            arb.reset()
    # time.sleep(2)
    
    