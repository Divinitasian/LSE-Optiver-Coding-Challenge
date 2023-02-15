import unittest
import libs
from marketmaking import best_quote_credit_assigning
from optibook.synchronous_client import Exchange
from market_maker import OptionMarketMaker

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
        
    def test_OptionMarketMaker_init_(self):
        option_id = libs.option_ids[0]
        option = exchange.get_instruments()[option_id]
        omm = OptionMarketMaker(option)
        print(omm.primal.instrument_id)
        print(omm.primal.base_instrument_id)
        
        
    def test_OptionMarketMaker__calculate_theoretical_option_value(self):
        option_id = libs.option_ids[0]
        option = exchange.get_instruments()[option_id]
        omm = OptionMarketMaker(option)
        stock_value = 25.8
        print(omm._calculate_theoretical_option_value(stock_value))
        
        
    def test_OptionMarketMaker__compute_fair_quotes(self):
        option_id = libs.option_ids[1]
        option = exchange.get_instruments()[option_id]
        omm = OptionMarketMaker(option)     
        print(omm.compute_fair_quotes(25.1, 25.3))