"""
Receive trader orders and send/cancel/amend the orders to the exchange.
"""
import numpy
from typing import Dict, Tuple, List
from optibook.common_types import Instrument, OrderStatus
from optibook.synchronous_client import Exchange

class ExecutionTrader:
    def __init__(
        self, 
        instrument: Instrument,
    ) -> None:
        self.instrument = instrument

    def action(
        self,
        trader_orders: Tuple[OrderStatus],
        outstanding_orders: Dict[int, OrderStatus]
    ) -> tuple:
        bid_order, ask_order = trader_orders
        self.to_cancel = []
        self.to_insert = {bid_order: 1, ask_order: 1}
        for order_id, order_status in outstanding_orders.items():
            if bid_order == order_status:
                self.to_insert[bid_order] = max(0, self.to_insert[bid_order] - 1)
            elif ask_order == order_status:
                self.to_insert[ask_order] = max(0, self.to_insert[ask_order] - 1)
            else:
                self.to_cancel.append(order_id)

    def insert_orders(self) -> List[OrderStatus]:
        return [order for order, count in self.to_insert.items() if count > 0 ]
    
    def cancel_orders(self) -> List[int]:
        return self.to_cancel

        



