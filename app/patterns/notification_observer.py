"""
OBSERVER DESIGN PATTERN
========================
Problem : Many events (new order, new message, delivery, review)
          must trigger notifications. Hardcoding these calls
          everywhere creates tight coupling.
Solution: Events are published to a NotificationPublisher.
          Observers subscribe and react independently.

Subject (Publisher) : NotificationPublisher
Observer Interface  : NotificationObserver
Concrete Observers  : DatabaseNotificationObserver,
                      SocketIONotificationObserver,
                      EmailNotificationObserver
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# EVENT  – what gets passed to every observer
# ---------------------------------------------------------------
@dataclass
class NotificationEvent:
    event_type:  str           # order_placed | message_sent | delivered | etc.
    recipient_id: int          # who should receive the notification
    actor_name:  str           # who triggered it ("Ali Hassan")
    title:       str
    body:        str
    link:        str = ""
    data:        Dict[str, Any] = None   # extra payload for SocketIO

    def __post_init__(self):
        if self.data is None:
            self.data = {}


# ---------------------------------------------------------------
# ABSTRACT OBSERVER
# ---------------------------------------------------------------
class NotificationObserver(ABC):

    @abstractmethod
    def update(self, event: NotificationEvent):
        """Called by the publisher when an event occurs."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


# ---------------------------------------------------------------
# CONCRETE OBSERVER 1 – saves to DB
# ---------------------------------------------------------------
class DatabaseNotificationObserver(NotificationObserver):

    def update(self, event: NotificationEvent):
        try:
            from app.models.notification import NotificationModel
            NotificationModel.create(
                user_id    = event.recipient_id,
                notif_type = event.event_type,
                title      = event.title,
                body       = event.body,
                link       = event.link,
            )
            logger.debug(f"[DB Notif] → user {event.recipient_id}: "
                         f"{event.title}")
        except Exception as e:
            logger.error(f"DatabaseNotificationObserver error: {e}")

    def get_name(self) -> str:
        return "DatabaseObserver"


# ---------------------------------------------------------------
# CONCRETE OBSERVER 2 – real-time push via SocketIO
# ---------------------------------------------------------------
class SocketIONotificationObserver(NotificationObserver):

    def update(self, event: NotificationEvent):
        try:
            from app import socketio
            payload = {
                "type":  event.event_type,
                "title": event.title,
                "body":  event.body,
                "link":  event.link,
                **event.data,
            }
            room = f"user_{event.recipient_id}"
            socketio.emit("notification", payload, room=room)
            logger.debug(f"[SocketIO Notif] → room {room}: {event.title}")
        except Exception:
            pass  # SocketIO not available outside app context – skip silently

    def get_name(self) -> str:
        return "SocketIOObserver"


# ---------------------------------------------------------------
# CONCRETE OBSERVER 3 – email (only for critical events)
# ---------------------------------------------------------------
class EmailNotificationObserver(NotificationObserver):

    CRITICAL_EVENTS = {"order_placed", "order_completed", "dispute_raised"}

    def update(self, event: NotificationEvent):
        if event.event_type not in self.CRITICAL_EVENTS:
            return   # only send emails for critical events
        try:
            from app.models.user import UserModel
            user = UserModel.get_by_id(event.recipient_id)
            if not user or not user.email:
                return
            # In production, integrate Flask-Mail here.
            # For now we just log.
            logger.info(
                f"[Email Notif] → {user.email} | "
                f"Subject: {event.title}"
            )
        except Exception as e:
            logger.error(f"EmailNotificationObserver error: {e}")

    def get_name(self) -> str:
        return "EmailObserver"


# ---------------------------------------------------------------
# PUBLISHER (Subject)
# ---------------------------------------------------------------
class NotificationPublisher:
    """
    Singleton-style publisher.
    All parts of the app call NotificationPublisher.notify()
    to fire an event. Registered observers react automatically.
    """

    _observers: List[NotificationObserver] = []
    _initialized: bool = False

    @classmethod
    def initialize(cls):
        """Register default observers. Call once at app startup."""
        if cls._initialized:
            return
        cls._observers = [
            DatabaseNotificationObserver(),
            SocketIONotificationObserver(),
            EmailNotificationObserver(),
        ]
        cls._initialized = True
        logger.info("NotificationPublisher initialized with "
                    f"{len(cls._observers)} observers.")

    @classmethod
    def subscribe(cls, observer: NotificationObserver):
        if observer not in cls._observers:
            cls._observers.append(observer)

    @classmethod
    def unsubscribe(cls, observer: NotificationObserver):
        cls._observers = [o for o in cls._observers if o is not observer]

    @classmethod
    def notify(cls, event: NotificationEvent):
        """Broadcast event to all registered observers."""
        if not cls._initialized:
            cls.initialize()
        for observer in cls._observers:
            try:
                observer.update(event)
            except Exception as e:
                logger.error(
                    f"Observer {observer.get_name()} failed: {e}")

    @classmethod
    def get_observer_names(cls) -> List[str]:
        return [o.get_name() for o in cls._observers]


# ---------------------------------------------------------------
# CONVENIENCE FUNCTIONS  – used by controllers
# ---------------------------------------------------------------
def notify_new_order(buyer_name: str, seller_id: int,
                     gig_title: str, order_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "order_placed",
        recipient_id = seller_id,
        actor_name   = buyer_name,
        title        = "New Order Received! 🎉",
        body         = f"{buyer_name} placed an order for '{gig_title}'",
        link         = f"/chat/{order_id}",
        data         = {"order_id": order_id},
    ))


def notify_new_message(sender_name: str, recipient_id: int,
                       order_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "message_sent",
        recipient_id = recipient_id,
        actor_name   = sender_name,
        title        = f"New message from {sender_name}",
        body         = "You have a new message.",
        link         = f"/chat/{order_id}",
        data         = {"order_id": order_id},
    ))


def notify_order_delivered(seller_name: str, buyer_id: int,
                           order_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "order_delivered",
        recipient_id = buyer_id,
        actor_name   = seller_name,
        title        = "Work Delivered! ✅",
        body         = f"{seller_name} has delivered your order. Please review.",
        link         = f"/order-status/{order_id}",
        data         = {"order_id": order_id},
    ))


def notify_order_completed(buyer_name: str, seller_id: int,
                           amount: float, order_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "order_completed",
        recipient_id = seller_id,
        actor_name   = buyer_name,
        title        = "Order Completed! 💰",
        body         = (f"{buyer_name} approved your delivery. "
                        f"{amount:.0f} coins added to your wallet."),
        link         = f"/wallet",
        data         = {"order_id": order_id, "amount": amount},
    ))


def notify_new_bid(seller_name: str, buyer_id: int,
                   project_title: str, project_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "bid_placed",
        recipient_id = buyer_id,
        actor_name   = seller_name,
        title        = "New Bid on Your Project 📩",
        body         = f"{seller_name} placed a bid on '{project_title}'",
        link         = f"/projects/{project_id}",
        data         = {"project_id": project_id},
    ))


def notify_bid_accepted(buyer_name: str, seller_id: int,
                        order_id: int):
    NotificationPublisher.notify(NotificationEvent(
        event_type   = "bid_accepted",
        recipient_id = seller_id,
        actor_name   = buyer_name,
        title        = "Your Bid Was Accepted! 🎯",
        body         = f"{buyer_name} accepted your bid. Check the chat.",
        link         = f"/chat/{order_id}",
        data         = {"order_id": order_id},
    ))