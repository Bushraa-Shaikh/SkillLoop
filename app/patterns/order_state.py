"""
STATE DESIGN PATTERN
====================
Problem : An Order moves through Pending → InProgress → Delivered
          → Completed. Each state allows different actions and
          transitions. If/else chains become unmaintainable.
Solution: Each state is a class. The Order context delegates
          behaviour to its current state object.

Context       : OrderContext
State Interface: OrderState (abstract)
Concrete States: PendingState, InProgressState, DeliveredState,
                 CompletedState, CancelledState, DisputedState
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------
# ABSTRACT STATE
# ---------------------------------------------------------------
class OrderState(ABC):

    @abstractmethod
    def start_work(self, order) -> str:
        pass

    @abstractmethod
    def deliver(self, order, delivery_link: str) -> str:
        pass

    @abstractmethod
    def approve(self, order) -> str:
        pass

    @abstractmethod
    def cancel(self, order) -> str:
        pass

    @abstractmethod
    def dispute(self, order) -> str:
        pass

    @abstractmethod
    def get_status(self) -> str:
        pass

    def _invalid(self, action: str) -> str:
        return (f"Action '{action}' is not allowed "
                f"in state '{self.get_status()}'.")


# ---------------------------------------------------------------
# CONCRETE STATES
# ---------------------------------------------------------------
class PendingState(OrderState):
    """Order placed, seller has not started yet."""

    def start_work(self, order) -> str:
        order.set_state(InProgressState())
        return "Order is now In Progress."

    def deliver(self, order, delivery_link: str) -> str:
        return self._invalid("deliver")

    def approve(self, order) -> str:
        return self._invalid("approve")

    def cancel(self, order) -> str:
        order.set_state(CancelledState())
        return "Order has been Cancelled."

    def dispute(self, order) -> str:
        return self._invalid("dispute")

    def get_status(self) -> str:
        return "Pending"


class InProgressState(OrderState):
    """Seller is working on the order."""

    def start_work(self, order) -> str:
        return self._invalid("start_work")

    def deliver(self, order, delivery_link: str) -> str:
        order.delivery_link = delivery_link
        order.set_state(DeliveredState())
        return "Work delivered. Waiting for buyer approval."

    def approve(self, order) -> str:
        return self._invalid("approve")

    def cancel(self, order) -> str:
        order.set_state(CancelledState())
        return "Order has been Cancelled."

    def dispute(self, order) -> str:
        order.set_state(DisputedState())
        return "Order is now Disputed."

    def get_status(self) -> str:
        return "InProgress"


class DeliveredState(OrderState):
    """Seller marked as delivered, buyer reviewing."""

    def start_work(self, order) -> str:
        return self._invalid("start_work")

    def deliver(self, order, delivery_link: str) -> str:
        # Allow re-delivery (revision)
        order.delivery_link = delivery_link
        return "Delivery updated."

    def approve(self, order) -> str:
        order.set_state(CompletedState())
        return "Order Completed! Coins released to seller."

    def cancel(self, order) -> str:
        return self._invalid("cancel")

    def dispute(self, order) -> str:
        order.set_state(DisputedState())
        return "Order is now Disputed."

    def get_status(self) -> str:
        return "Delivered"


class CompletedState(OrderState):
    """Order approved and finished. Terminal state."""

    def start_work(self, order) -> str:
        return self._invalid("start_work")

    def deliver(self, order, delivery_link: str) -> str:
        return self._invalid("deliver")

    def approve(self, order) -> str:
        return self._invalid("approve")

    def cancel(self, order) -> str:
        return self._invalid("cancel")

    def dispute(self, order) -> str:
        return self._invalid("dispute")

    def get_status(self) -> str:
        return "Completed"


class CancelledState(OrderState):
    """Order was cancelled. Terminal state."""

    def start_work(self, order) -> str:
        return self._invalid("start_work")

    def deliver(self, order, delivery_link: str) -> str:
        return self._invalid("deliver")

    def approve(self, order) -> str:
        return self._invalid("approve")

    def cancel(self, order) -> str:
        return "Order is already Cancelled."

    def dispute(self, order) -> str:
        return self._invalid("dispute")

    def get_status(self) -> str:
        return "Cancelled"


class DisputedState(OrderState):
    """Dispute raised – admin must resolve."""

    def start_work(self, order) -> str:
        return self._invalid("start_work")

    def deliver(self, order, delivery_link: str) -> str:
        return self._invalid("deliver")

    def approve(self, order) -> str:
        # Admin can force-complete
        order.set_state(CompletedState())
        return "Dispute resolved. Order Completed."

    def cancel(self, order) -> str:
        # Admin can force-cancel and refund
        order.set_state(CancelledState())
        return "Dispute resolved. Order Cancelled."

    def dispute(self, order) -> str:
        return "Order is already under dispute."

    def get_status(self) -> str:
        return "Disputed"


# ---------------------------------------------------------------
# STATE MAP  – string → State class
# ---------------------------------------------------------------
STATE_MAP = {
    "Pending":    PendingState,
    "InProgress": InProgressState,
    "Delivered":  DeliveredState,
    "Completed":  CompletedState,
    "Cancelled":  CancelledState,
    "Disputed":   DisputedState,
}


def state_from_string(status: str) -> OrderState:
    """Restore a state object from a status string (e.g. loaded from DB)."""
    cls = STATE_MAP.get(status)
    if not cls:
        raise ValueError(f"Unknown order status: '{status}'")
    return cls()


# ---------------------------------------------------------------
# CONTEXT  – the Order object that delegates to current state
# ---------------------------------------------------------------
class OrderContext:
    """
    Context that holds the current state and delegates all
    order actions to it.

    Usage:
        ctx = OrderContext(order_id=1, status='Pending')
        msg = ctx.start_work()       # → "Order is now In Progress."
        msg = ctx.deliver('https://drive.google.com/...')
        msg = ctx.approve()          # → "Order Completed! ..."
    """

    def __init__(self, order_id: int, status: str = "Pending",
                 delivery_link: str = None):
        self.order_id      = order_id
        self._state        = state_from_string(status)
        self.delivery_link = delivery_link
        self._history      = [status]   # audit trail

    def set_state(self, new_state: OrderState):
        self._state = new_state
        self._history.append(new_state.get_status())

    # -- Delegated actions --------------------------------------

    def start_work(self) -> str:
        msg = self._state.start_work(self)
        self._persist()
        return msg

    def deliver(self, delivery_link: str) -> str:
        msg = self._state.deliver(self, delivery_link)
        self._persist()
        return msg

    def approve(self) -> str:
        msg = self._state.approve(self)
        self._persist()
        return msg

    def cancel(self) -> str:
        msg = self._state.cancel(self)
        self._persist()
        return msg

    def dispute(self) -> str:
        msg = self._state.dispute(self)
        self._persist()
        return msg

    # -- Queries ------------------------------------------------

    @property
    def status(self) -> str:
        return self._state.get_status()

    @property
    def history(self) -> list:
        return self._history.copy()

    def can_start_work(self) -> bool:
        return isinstance(self._state, PendingState)

    def can_deliver(self) -> bool:
        return isinstance(self._state, (InProgressState, DeliveredState))

    def can_approve(self) -> bool:
        return isinstance(self._state, DeliveredState)

    def can_cancel(self) -> bool:
        return isinstance(self._state, (PendingState, InProgressState))

    def is_terminal(self) -> bool:
        return isinstance(self._state, (CompletedState, CancelledState))

    # -- DB persistence -----------------------------------------

    def _persist(self):
        """Save current status to database."""
        try:
            from app.models.order import OrderModel
            OrderModel.update_status(self.order_id, self.status)
            if self.delivery_link:
                OrderModel.set_delivery_link(
                    self.order_id, self.delivery_link)
        except Exception:
            pass   # DB not available during unit tests