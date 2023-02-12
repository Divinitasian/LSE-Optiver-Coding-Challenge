import unittest
import libs
from market_maker import MarketMaker, _make_market_profitable
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()


option_ids = [
    'NVDA_202306_020C',
    'NVDA_202306_020P',
    'NVDA_202306_030C',
    'NVDA_202306_030P',
    'NVDA_202306_040C',
    'NVDA_202306_040P',
    'NVDA_202306_050C',
    'NVDA_202306_050P',
    ]
future_ids = [
    'NVDA_202306_F',
    'NVDA_202309_F',
    'NVDA_202312_F'
    ]
stock_ids = [
    'NVDA_DUAL'
    ]

class TestMarketMaker(unittest.TestCase):
    def test_set_sides(self):
        direction = 'short'
        trader = MarketMaker(
            stock_ids[0],
            'NVDA'
            )
        trader.set_sides(direction)
        self.assertListEqual(
            trader.sides, 
            ['ask']
            )
            
    
    def test_collect(self):
        trader = MarketMaker(
            option_ids[0],
            'NVDA'
            )
        trader.collect(exchange)
        print(trader.reference)
        
        
    def test_price(self):
        trader = MarketMaker(
            stock_ids[0],
            'NVDA'
            )
        trader.collect(exchange)
        trader.price()
        print(trader.theoretical_prices)
        
        
    def test_lib_get_best_quotes(self):
        side = 'bid'
        instrument = stock_ids[0]
        order_book = None
        # order_book = exchange.get_last_price_book(instrument)
        
        quote = libs.get_best_quote(order_book, side)
        print(f"The best {side} quote of {instrument} is {quote}.")
        
        
    def test_get_valid_volume(self):
        volume = 200
        position = 80
        position_limit = 80
        side = 'ask'
        volume = libs.get_valid_volume(
            volume, 
            position, 
            position_limit, 
            side
            )
        print(f"The valide volume to {side} is {volume}.")
        
    def test_make_market_profitable(self):
        side = 'bid'
        position = -100
        position_limit = 80
        theoretical_price = 32
        order_book = exchange.get_last_price_book(stock_ids[0])
        best_quote = libs.get_best_quote(order_book, side)
        profitable, price, volume = _make_market_profitable(
                theoretical_price,
                best_quote,
                side,
                libs.TICK_SIZE,
                0.05
                )
        volume = libs.get_valid_volume(
            volume, 
            position, 
            position_limit, 
            side
            )
        print(f"Is market making on {side} side profitable: {profitable}.")
        print(f"The new limit order to send is {volume}@{price}.")
        