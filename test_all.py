import unittest
import libs
from trade import underlying_hash, market_makers_hash
from optibook.synchronous_client import Exchange
from market_maker import OptionMarketMaker

exchange = Exchange()
exchange.connect()


class TestMarketMaker:
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
        
    def test_trade_load(self):
        all_instruments = exchange.get_instruments()
        underlying_dict = underlying_hash(all_instruments)
        assert underlying_dict['CSCO'] == 'CSCO'
        print(underlying_dict)
        
        
    def test_trade_init(self):
        all_instruments = exchange.get_instruments()
        underlying_dict = underlying_hash(all_instruments)
        market_makers_dict = market_makers_hash(all_instruments, underlying_dict)
        print(market_makers_dict)
        
        
    def test_libs_detect(self):
        best_bid_price = .1
        best_ask_price = .2
        theoretical_bid_price = .05
        theoretical_ask_price = .09
        assert libs.detect_arbitrage(best_bid_price, best_ask_price, theoretical_bid_price, theoretical_ask_price) == 'ask'
        
        best_bid_price = .1
        best_ask_price = .2
        theoretical_bid_price = .3
        theoretical_ask_price = .4
        assert libs.detect_arbitrage(best_bid_price, best_ask_price, theoretical_bid_price, theoretical_ask_price) == 'bid'
        