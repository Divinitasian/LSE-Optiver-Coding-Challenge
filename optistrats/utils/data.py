"""
Fetch the data from the exchange
"""
from typing import Dict
from optibook.synchronous_client import Exchange
from optibook.common_types import Instrument, PriceBook, OrderStatus


class DataBase:
    def __init__(self, exchange: Exchange) -> None:
        self.exchange = exchange
        # static
        self.instruments = {
            instrument: 1
            for instrument in self.exchange.get_instruments().values()
        }
        # dynamic
        self.positions = None
        self.last_price_books = None
        self.outstanding_orders = None
        self.tradable_instruments = None
        self.fetch()
        
    def fetch(self) -> None:
        positions = self.exchange.get_positions()
        self.positions = {
            instrument: positions[instrument.instrument_id]
            for instrument in self.instruments
        }
        self.last_price_books = {
            instrument: self.exchange.get_last_price_book(instrument.instrument_id)
            for instrument in self.instruments
        }
        self.outstanding_orders = {
            instrument: self.exchange.get_outstanding_orders(instrument.instrument_id)
            for instrument in self.instruments
        }
        self.tradable_instruments = {
            instrument: 1
            for instrument in self.exchange.get_tradable_instruments().values()
        }

    def get_instruments(self) -> Dict[Instrument, int]:
        return self.instruments
    
    def get_position(self, instrument: Instrument) -> int:
        return self.positions[instrument]
    
    def get_last_price_book(self, instrument: Instrument) -> PriceBook:
        return self.last_price_books[instrument]
    
    def get_outstanding_order(self, instrument: Instrument) -> Dict[int, OrderStatus]:
        return self.outstanding_orders[instrument]
    
    def get_tradable_instruments(self) -> Dict[Instrument, int]:
        return self.tradable_instruments
