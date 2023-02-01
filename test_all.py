from market_maker import LinearDerivativeMarketMaker, OptionMarketMaker
from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()

class TestMarketMaker:
    def test_update(self):
        instrument_id, hedge_id = 'NVDA_DUAL', 'NVDA'
        # First transaction
        market_maker = LinearDerivativeMarketMaker(instrument_id, hedge_id)
        theoretical_bidprice, theoretical_askprice = 12, 19
        credit, volume = 0.15, 150
        market_maker.update(exchange, theoretical_bidprice, theoretical_askprice, credit, volume)
        print(f'Outstanding orders:')
        print(exchange.get_outstanding_orders(instrument_id))
        # Second transaction
        theoretical_bidprice, theoretical_askprice = 11, 20
        credit, volume = 0.3, 180
        market_maker.update(exchange, theoretical_bidprice, theoretical_askprice, credit, volume)
        print(f'Outstanding orders:')
        print(exchange.get_outstanding_orders(instrument_id))
        
    
    def test_hedge(self):
        instrument_id, hedge_id = 'NVDA_DUAL', 'NVDA'
        market_maker = LinearDerivativeMarketMaker(instrument_id, hedge_id)
        delta = market_maker.compute_delta(exchange)
        market_maker.hedge(exchange, delta)
        print(exchange.get_positions())
        
        
    def test_option_price(self):
        instrument_id, hedge_id = 'NVDA_202306_030C', 'NVDA'
        market_maker = OptionMarketMaker(instrument_id, hedge_id)
        bid_price, ask_price = market_maker.get_fair_prices(exchange)
        print(f'The fair bid price is {bid_price:.2f}.')
        print(f'The fair ask price is {ask_price:.2f}.')
        

    def test_option_delta(self):
        instrument_id, hedge_id = 'NVDA_202306_040P', 'NVDA'
        exchange.insert_order(instrument_id=instrument_id, 
            price=1000000, 
            volume=2, 
            side='bid', 
            order_type='ioc'
            )
        market_maker = OptionMarketMaker(instrument_id, hedge_id)
        delta = market_maker.compute_delta(exchange)
        print(f'The delta of position in {instrument_id} is {delta:.2f}.')
        exchange.insert_order(instrument_id=instrument_id, 
            price=1, 
            volume=3, 
            side='ask', 
            order_type='ioc'
            )
        market_maker = OptionMarketMaker(instrument_id, hedge_id)
        delta = market_maker.compute_delta(exchange)
        print(f'The delta of position in {instrument_id} is {delta:.2f}.')
        