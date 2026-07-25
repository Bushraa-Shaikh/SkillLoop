"""
Message Model – chat messages tied to orders.
"""
from app.utils.db import execute_query


class MessageModel:

    @staticmethod
    def get_by_order(order_id: int) -> list:
        rows = execute_query(
            """
            SELECT m.*, u.name AS sender_name,
                   u.profile_pic AS sender_pic
            FROM Messages m
            JOIN Users u ON u.user_id = m.sender_id
            WHERE m.order_id = ?
            ORDER BY m.sent_at ASC
            """,
            (order_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def send(order_id: int, sender_id: int,
             body: str, drive_link: str = None) -> int:
        msg_id = execute_query(
            """
            INSERT INTO Messages (order_id, sender_id, body, drive_link)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, sender_id, body, drive_link)
        )
        return msg_id

    @staticmethod
    def mark_read(order_id: int, reader_id: int):
        """Mark all messages in this order as read (except own)."""
        execute_query(
            "UPDATE Messages SET is_read = 1 "
            "WHERE order_id = ? AND sender_id != ?",
            (order_id, reader_id)
        )

    @staticmethod
    def unread_count(user_id: int) -> int:
        """Total unread messages across all orders for this user."""
        row = execute_query(
            """
            SELECT COUNT(*) AS cnt FROM Messages m
            JOIN Orders o ON o.order_id = m.order_id
            WHERE (o.buyer_id = ? OR o.seller_id = ?)
              AND m.sender_id != ?
              AND m.is_read = 0
            """,
            (user_id, user_id, user_id), fetch="one"
        )
        return row["cnt"] if row else 0

    @staticmethod
    def get_conversations(user_id: int) -> list:
        """Latest message per order for the inbox view."""
        rows = execute_query(
            """
            SELECT o.order_id, o.status,
                   g.title AS gig_title,
                   other.name AS other_name,
                   other.profile_pic AS other_pic,
                   last_msg.body AS last_body,
                   last_msg.sent_at AS last_sent,
                   unread.cnt AS unread_count
            FROM Orders o
            JOIN Gigs g ON g.gig_id = o.gig_id
            JOIN Users other ON other.user_id =
                CASE WHEN o.buyer_id = ? THEN o.seller_id ELSE o.buyer_id END
            OUTER APPLY (
                SELECT TOP 1 body, sent_at
                FROM Messages
                WHERE order_id = o.order_id
                ORDER BY sent_at DESC
            ) last_msg
            OUTER APPLY (
                SELECT COUNT(*) AS cnt
                FROM Messages
                WHERE order_id = o.order_id
                  AND sender_id != ?
                  AND is_read = 0
            ) unread
            WHERE o.buyer_id = ? OR o.seller_id = ?
            ORDER BY last_msg.sent_at DESC
            """,
            (user_id, user_id, user_id, user_id), fetch="all"
        )
        return rows or []