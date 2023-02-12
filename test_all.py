import unittest
import libs
from market_maker import MarketMaker
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
        
        
    # def test_lib_market_making_profitable(self):
    #     stock_book = exchange.get_last_price_book('NVDA')
    #     theoretical_price = stock_book.asks[0].price
    #     print(f'NVDA: ask')
    #     dual_book = exchange.get_last_price_book('NVDA_DUAL')
    #     quote = dual_book if not dual_book else dual_book.asks[0].price
    #     assert libs.market_making_profitable(
    #         theoretical_price,
    #         quote, 
    #         'ask',
    #         libs.TICK_SIZE
    #         ) == True
        