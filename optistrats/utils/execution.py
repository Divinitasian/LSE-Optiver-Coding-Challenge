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

    def receive(
        self,
        limit_orders: Iterable[LimitOrder],
        outstanding_orders: Dict[int, OrderStatus]
    ) -> None:
        """Receive the limit orders and combine with the outstanding orders.

        Parameters
        ----------
        limit_orders
            a sequence of limit orders.
        outstanding_orders
            the outstanding orders on the market.
        """
        bid_order, ask_order = limit_orders
        self.to_cancel = []
        self.to_insert = Counter(limit_orders)
        for order_id, order_status in outstanding_orders.items():
            if bid_order == order_status:
                self.to_insert.subtract(bid_order)
            elif ask_order == order_status:
                self.to_insert.subtract(ask_order)
            else:
                self.to_cancel.append(order_id)

    def insert_orders(self) -> List[OrderStatus]:
        """The new order to be inserted.

        Returns
        -------
            a list of orders in the exchange-acceptable format.
        """
        return [order for order, count in self.to_insert.items() if count > 0 ]
    
    def cancel_orders(self) -> List[int]:
        """The old orders to be cancelled.

        Returns
        -------
            a list of order id.
        """
        return self.to_cancel
