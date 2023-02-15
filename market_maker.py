from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date
from optibook.common_types import OptionKind

class OptionMarketMaker:
    def __init__(self, option):
        self.primal = option
        self.dual_id = option.base_instrument_id
        
        
    def _calculate_theoretical_option_value(self, stock_value, interest_rate, volatility):
        """
        This function calculates the current fair call or put value based on Black & Scholes assumptions.
    
        stock_value:             -  Assumed stock value when calculating the Black-Scholes value
        interest_rate:           -  Assumed interest rate when calculating the Black-Scholes value
        volatility:              -  Assumed volatility of when calculating the Black-Scholes value
        """
        expiry = self.primal.expiry
        strike = self.primal.strike
        option_kind = self.primal.option_kind
        time_to_expiry = calculate_current_time_to_date(expiry)
    
        if option_kind == OptionKind.CALL:
            option_value = call_value(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)
        elif option_kind == OptionKind.PUT:
            option_value = put_value(S=stock_value, K=strike, T=time_to_expiry, r=interest_rate, sigma=volatility)
            
        return option_value
        
        
    def compute_fair_quotes(self, stock_bid_price, stock_ask_price, interest_rate, volatility):
        theoretical_value_1 = self._calculate_theoretical_option_value(
            stock_bid_price, 
            interest_rate, 
            volatility
            )
        theoretical_value_2 = self._calculate_theoretical_option_value(
            stock_ask_price, 
            interest_rate, 
            volatility
            )
        theoretical_bid_price = min(theoretical_value_1, theoretical_value_2)
        theoretical_ask_price = max(theoretical_value_1, theoretical_value_2)
        return theoretical_bid_price, theoretical_ask_price
        
        
    def select_credits(self, default):
        credit_bid = default
        credit_ask = default
        return credit_bid, credit_ask
    
    
    def select_volumes(self, default):
        volume_bid = default
        volume_ask = default
        return volume_bid, volume_ask
        
        