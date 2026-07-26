from simulation_engine.entities.order import Order, OrderStatus

from simulation_engine.config import PRODUCT_PRIORITIES
from simulation_engine.state import SimulationState


import pandas as pd


class OrderManager:
    """
    Manages customer orders throughout the simulation.
    """

    def __init__(self):
        self.next_order_id = 1

    # ---------------------------------------------------------
    # Create Order
    # ---------------------------------------------------------

    def create_order(
        self,
        state,
        customer_id,
        products,
        latitude,
        longitude,
    ):
        """
        Create a new customer order.
        """

        order = Order(
            order_id=self.next_order_id,
            customer_id=customer_id,
            created_time=state.current_time,
            products=products,
            latitude=latitude,
            longitude=longitude,
        )
        # define in config product priorities
        order.status = OrderStatus.PLACED

        state.orders[order.order_id] = order
        state.pending_orders[order.order_id] = order
        

        state.statistics["orders_created"] += 1

        state.log(
            f"Order {order.order_id} created."
        )

        self.next_order_id += 1

        return order

    # ---------------------------------------------------------
    # Process Orders
    # ---------------------------------------------------------

    def update_orders(
        self,
        state: SimulationState,
        order_zone_map: dict,
    ):

        for order in state.orders.values():
            
            order["priority_score"] = self.compute_priority_score(
                order,PRODUCT_PRIORITIES)

            info = order_zone_map.get(order.order_id)

            if info is None:
                continue

            order.h3_cell_7 = info["h3_cell_7"]
            order.h3_cell_8 = info["h3_cell_8"]
            order.zone_id = info["zone_id"]

    def update_order_status(
        self,
        state: SimulationState,
        order_id: int,
        status: OrderStatus,
    ):

        order = state.orders.get(order_id)

        if order is None:
            return

        order.status = status

        state.log(
            f"Order {order_id} -> {status.value}"
        )


    # ---------------------------------------------------------
    # Complete Order
    # ---------------------------------------------------------

    def complete_order(self, state, order_id):

        order = state.orders.get(order_id)

        if order is None:
            return

        order.status = OrderStatus.DELIVERED
        order.delivered_time = state.current_time

        if order_id in state.active_orders:
            state.active_orders.pop(order_id)

        state.completed_orders[order_id] = order

        state.statistics["orders_completed"] += 1

        state.log(f"Order {order_id} completed.")

    # ---------------------------------------------------------
    # Cancel Order
    # ---------------------------------------------------------

    def cancel_order(self, state, order_id):

        order = state.orders.get(order_id)

        if order is None:
            return

        order.status = "Cancelled"

        if order_id in state.pending_orders:
            state.pending_orders.pop(order_id)

        if order_id in state.active_orders:
            state.active_orders.pop(order_id)

        state.cancelled_orders[order_id] = order

        state.statistics["orders_cancelled"] += 1

        state.log(
            f"Order {order_id} cancelled."
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def get_order(self, state, order_id):

        return state.orders.get(order_id)

    def get_pending_orders(self, state):

        return state.pending_orders.values()

    def get_active_orders(self, state):

        return state.active_orders.values()

    def to_dataframe(
        self,
        state: SimulationState,
    ) -> pd.DataFrame:

        return pd.DataFrame(
            [
                order.to_dict()
                for order in state.orders.values()
            ]
        )

    def compute_priority_score(
        self,
        order: Order,
        product_priorities: dict[int, float],
    ) -> None:
        """
        Compute normalized priority score as the weighted mean
        of product priorities.
        """

        weighted_sum = 0.0
        total_quantity = 0

        for product_id, quantity in order.products.items():
            priority = product_priorities.get(product_id, 0.5)

            weighted_sum += quantity * priority
            total_quantity += quantity

        priority_score = (
            weighted_sum / total_quantity
            if total_quantity > 0
            else 0.0
        )

        return priority_score