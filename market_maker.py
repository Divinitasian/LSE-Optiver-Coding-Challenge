import datetime as dt
import time
import logging

from optibook.synchronous_client import Exchange
from optibook.common_types import InstrumentType, OptionKind

from math import floor, ceil
from black_scholes import call_value, put_value, call_delta, put_delta
from libs import calculate_current_time_to_date, check_and_get_best_bid_ask
from libs import round_down_to_tick, round_up_to_tick, clear_orders, clear_position
from libs import POSITION_LIMIT, TICK_SIZE, MAX_BUYING_PRICE, MIN_SELLING_PRICE
from libs import calculate_option_delta, calculate_theoretical_option_value
from libs import INTEREST_RATE, VOLATILITY


logging.getLogger('client').setLevel('ERROR')

