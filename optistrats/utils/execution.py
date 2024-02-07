"""
Receive trader orders and send/cancel/amend the orders to the exchange.
"""
from collections import Counter
from typing import Dict, Iterable, List
from optibook.common_types import Instrument, OrderStatus

from optistrats.types import LimitOrder


class ExecutionTrader:
    def __init__(
        self, 
        instrument: Instrument,
    ) -> None:
        self.instrument = instrument

    def minimize_cost(
        self,
        limit_orders: Iterable[LimitOrder],
        outstanding_orders: Dict[int, OrderStatus]
    ) -> None:
        """Minimize the trading costs by avoiding the redundant orders.

        Parameters
        ----------
        limit_orders
            a sequence of limit orders to send.
        outstanding_orders
            the outstanding orders on the market.
        """
        to_keep = set()
        limit_order_covered = set()
        unique_limit_orders =  Counter(limit_orders)
        for order_id, order_status in outstanding_orders.items():
            for limit_order in unique_limit_orders:
                if order_status == limit_order:
                    to_keep.add(order_id)
                    limit_order_covered.add(limit_order)

        self.to_cancel = [
            id 
            for id in outstanding_orders \
                if id not in to_keep
        ]
        self.to_insert = [
            limit_order
            for limit_order in unique_limit_orders \
                if limit_order not in limit_order_covered
        ]


    def insert_orders(self) -> List[OrderStatus]:
        """The new order to be inserted.

        Returns
        -------
            a list of orders in the exchange-acceptable format.
        """
        return [limit_order.to_order_status() for limit_order in self.to_insert]
    
    def cancel_orders(self) -> List[int]:
        """The old orders to be cancelled.

        Returns
        -------
            a list of order id.
        """
        return self.to_cancel
