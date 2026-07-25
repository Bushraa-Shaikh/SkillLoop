"""
Notification Model – system notifications for users.
Actual triggering is handled by the Observer pattern.
"""
from app.utils.db import execute_query


class NotificationModel:

    @staticmethod
    def create(user_id: int, notif_type: str,
               title: str, body: str = "", link: str = "") -> int:
        notif_id = execute_query(
            """
            INSERT INTO Notifications
                (user_id, type, title, body, link)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, notif_type, title, body, link)
        )
        return notif_id

    @staticmethod
    def get_by_user(user_id: int, limit: int = 20) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) * FROM Notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (limit, user_id), fetch="all"
        )
        return rows or []

    @staticmethod
    def mark_read(notif_id: int):
        execute_query(
            "UPDATE Notifications SET is_read = 1 WHERE notif_id = ?",
            (notif_id,)
        )

    @staticmethod
    def mark_all_read(user_id: int):
        execute_query(
            "UPDATE Notifications SET is_read = 1 WHERE user_id = ?",
            (user_id,)
        )

    @staticmethod
    def unread_count(user_id: int) -> int:
        row = execute_query(
            "SELECT COUNT(*) AS cnt FROM Notifications "
            "WHERE user_id = ? AND is_read = 0",
            (user_id,), fetch="one"
        )
        return row["cnt"] if row else 0

    @staticmethod
    def delete_old(days: int = 30):
        execute_query(
            "DELETE FROM Notifications "
            "WHERE created_at < DATEADD(DAY, -?, GETDATE())",
            (days,)
        )