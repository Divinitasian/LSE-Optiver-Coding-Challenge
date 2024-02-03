import unittest
import optistrats.utils as utils
from optistrats.scripts.run import underlying_hash, market_makers_hash
from optibook.synchronous_client import Exchange
from optistrats.strats.market_maker import OptionMarketMaker

from hyperparameter import trade_one_iteration

exchange = Exchange()
exchange.connect()


class TestMarketMaker:
    def test_OptionMarketMaker_init_(self):
        option_id = utils.option_ids[0]
        option = exchange.get_instruments()[option_id]
        omm = OptionMarketMaker(option)
        print(omm.primal.instrument_id)
        print(omm.primal.base_instrument_id)
        
        
    def test_OptionMarketMaker__calculate_theoretical_option_value(self):
        option_id = utils.option_ids[0]
        option = exchange.get_instruments()[option_id]
        omm = OptionMarketMaker(option)
        stock_value = 25.8
        print(omm._calculate_theoretical_option_value(stock_value))
        
        
    def test_OptionMarketMaker__compute_fair_quotes(self):
        option_id = utils.option_ids[1]
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
        assert utils.detect_arbitrage(best_bid_price, best_ask_price, theoretical_bid_price, theoretical_ask_price) == 'ask'
        
        best_bid_price = .1
        best_ask_price = .2
        theoretical_bid_price = .3
        theoretical_ask_price = .4
        assert utils.detect_arbitrage(best_bid_price, best_ask_price, theoretical_bid_price, theoretical_ask_price) == 'bid'
        
        
class TestHyperparameterSearch:
    def test_trade_one_iteration(self):
        iteration = 1
        market_maker = OptionMarketMaker(exchange.get_instruments()['NVDA_202306_050P'])
        underlying_id = 'NVDA'
        wait_time = .2
        credit_ic_mode = 'constant'
        volume_ic_mode = 'linear-deprecate'
        pnl = trade_one_iteration(
            iteration, 
            market_maker, 
            exchange, 
            underlying_id, 
            wait_time, 
            credit_ic_mode, 
            volume_ic_mode
            )
        print(f'\n - The current PnL is {pnl}.')