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
        self.instruments = set(self.exchange.get_instruments().values())
        # dynamic
        self.positions = None
        self.last_price_books = None
        self.outstanding_orders = None
        self.tradable_instruments = None
        self.fetch()
        
    def fetch(self) -> None:
        """Download the latest market information from the exchange
        """
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
        self.tradable_instruments = set(self.exchange.get_tradable_instruments().values())

    def get_instruments(self) -> Dict[Instrument, int]:
        """Returns all existing instruments on the exchange

        Returns
        -------
        set[Instrument]
            a set of the instrument definition.
        """
        return self.instruments
    
    def get_position(self, instrument: Instrument) -> int:
        """Returns the position of the instrument

        Parameters
        ----------
        instrument
            Instrument object   

        Returns
        -------
            current position
        """
        return self.positions[instrument]
    
    def get_last_price_book(self, instrument: Instrument) -> PriceBook:
        """Returns the last received limit order book state for an instrument.

        Parameters
        ----------
        instrument: Instrument
            The instrument to obtain the limit order book for.

        Returns
        -------
        PriceBook
            Returns the last received limit order book state for an instrument.
        """
        return self.last_price_books[instrument]
    
    def get_outstanding_order(self, instrument: Instrument) -> Dict[int, OrderStatus]:
        """
        Returns the client's currently outstanding limit orders on an instrument.

        Parameters
        ----------
        instrument: Instrument
            The instrument to obtain outstanding orders for.

        Returns
        -------
        typing.Dict[int, OrderStatus]
            Dictionary mapping order_id to OrderStatus objects representing the client's currently outstanding limit
            orders on an instrument.
        """
        return self.outstanding_orders[instrument]
    
    def get_tradable_instruments(self) -> Dict[Instrument, int]:
        """
        Returns all tradable instruments on the exchange.
        This excludes instruments which are expired or for which trading is paused.

        Returns
        -------
        set[Instrument]
            a set of the instrument definition.
        """
        return self.tradable_instruments
