import unittest
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
            option_ids[-1],
            'NVDA'
            )
        trader.set_sides(direction)
        self.assertListEqual(
            trader.sides, 
            ['bid']
            )
            
    
    def test_collect(self):
        direction = 'short'
        trader = MarketMaker(
            option_ids[0],
            'NVDA'
            )
        trader.collect(exchange)
        print(trader.reference_prices)
        
        