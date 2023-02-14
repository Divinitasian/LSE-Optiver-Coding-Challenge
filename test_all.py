import unittest
import libs
from market_maker import best_quote_credit_assigning
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()


class TestMarketMaker:
    def test_best_quote_credit_assigning(self):
        best_quote_price = 9.8
        theoretical_price = 10
        default_credit = 0.03
        side = 'ask'
        tick_size = 0.1
        assert best_quote_credit_assigning(
            best_quote_price,
            theoretical_price,
            default_credit,
            side,
            tick_size
            ) == 0.03
        
        
        
        
        