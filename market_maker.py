from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, round_down_to_tick, round_up_to_tick
from libs import get_bid_ask
from libs import INTEREST_RATE, VOLATILITY
from optibook.common_types import OptionKind

class OptionMarketMaker:
    def __init__(self, option):
        self.primal = option
        self.dual_id = option.base_instrument_id

        self.interest_rate = INTEREST_RATE
        self.volatility = VOLATILITY
        
        self.credit_bid = 0.03
        self.credit_ask = 0.03

        self.volume_bid = 100
        self.volume_ask = 100
        
        
    def _calculate_theoretical_option_value(self, stock_value):
        """
        This function calculates the current fair call or put value based on Black & Scholes assumptions.
    
        stock_value:             -  Assumed stock value when calculating the Black-Scholes value
        """
        expiry = self.primal.expiry
        strike = self.primal.strike
        option_kind = self.primal.option_kind
        time_to_expiry = calculate_current_time_to_date(expiry)
    
        if option_kind == OptionKind.CALL:
            option_value = call_value(S=stock_value, K=strike, T=time_to_expiry, r=self.interest_rate, sigma=self.volatility)
        elif option_kind == OptionKind.PUT:
            option_value = put_value(S=stock_value, K=strike, T=time_to_expiry, r=self.interest_rate, sigma=self.volatility)
            
        return option_value
        
        
        
    def compute_fair_quotes(self, stock_bid_price, stock_ask_price):
        theoretical_value_1 = self._calculate_theoretical_option_value(
            stock_bid_price
            )
        theoretical_value_2 = self._calculate_theoretical_option_value(
            stock_ask_price
            )
        theoretical_bid_price = min(theoretical_value_1, theoretical_value_2)
        theoretical_ask_price = max(theoretical_value_1, theoretical_value_2)
        return theoretical_bid_price, theoretical_ask_price
        
        
    def get_traded_orders(self, exchange):
        """
        Print any new trades
        """
        trades = exchange.poll_new_trades(instrument_id=self.primal.instrument_id)
        for trade in trades:
            print(f'- Last period, traded {trade.volume} lots in {self.primal.instrument_id} at price {trade.price:.2f}, side {trade.side}.')
        
        








