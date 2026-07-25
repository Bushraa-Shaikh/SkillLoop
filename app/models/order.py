"""
Order Model – wraps the Orders table.
Order lifecycle: Pending → InProgress → Delivered → Completed
"""
from app.utils.db import execute_query



class OrderModel:

    STATES = ["Pending", "InProgress", "Delivered", "Completed",
              "Cancelled", "Disputed"]

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    @staticmethod
    def get_by_id(order_id: int) -> dict:
        return execute_query(
            """
            SELECT o.*,
                   b.name AS buyer_name,  b.profile_pic AS buyer_pic,
                   b.email AS buyer_email,
                   s.name AS seller_name, s.profile_pic AS seller_pic,
                   s.email AS seller_email,
                   g.title AS gig_title,  g.thumbnail AS gig_thumbnail,
                   g.delivery_days
            FROM Orders o
            JOIN Users b ON b.user_id = o.buyer_id
            JOIN Users s ON s.user_id = o.seller_id
            JOIN Gigs  g ON g.gig_id  = o.gig_id
            WHERE o.order_id = ?
            """,
            (order_id,), fetch="one"
        )

    @staticmethod
    def get_by_buyer(buyer_id: int) -> list:
        rows = execute_query(
            """
            SELECT o.*, g.title AS gig_title, g.thumbnail,
                   s.name AS seller_name, s.profile_pic AS seller_pic
            FROM Orders o
            JOIN Gigs  g ON g.gig_id  = o.gig_id
            JOIN Users s ON s.user_id = o.seller_id
            WHERE o.buyer_id = ?
            ORDER BY o.created_at DESC
            """,
            (buyer_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_by_seller(seller_id: int) -> list:
        rows = execute_query(
            """
            SELECT o.*, g.title AS gig_title, g.thumbnail,
                   b.name AS buyer_name, b.profile_pic AS buyer_pic
            FROM Orders o
            JOIN Gigs  g ON g.gig_id  = o.gig_id
            JOIN Users b ON b.user_id = o.buyer_id
            WHERE o.seller_id = ?
            ORDER BY o.created_at DESC
            """,
            (seller_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_active_by_seller(seller_id: int) -> list:
        rows = execute_query(
            """
            SELECT o.*, g.title AS gig_title,
                   b.name AS buyer_name
            FROM Orders o
            JOIN Gigs  g ON g.gig_id  = o.gig_id
            JOIN Users b ON b.user_id = o.buyer_id
            WHERE o.seller_id = ?
              AND o.status IN ('Pending','InProgress','Delivered')
            ORDER BY o.created_at DESC
            """,
            (seller_id,), fetch="all"
        )
        return rows or []

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    @staticmethod
    def create(gig_id: int, buyer_id: int, seller_id: int,
            amount: float, payment_method: str = "coins",
            requirements: str = "") -> int:
        try:
            from app.utils.db import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO Orders
                        (gig_id, buyer_id, seller_id, amount,
                        payment_method, requirements, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                    """,
                    (gig_id, buyer_id, seller_id, amount,
                    payment_method, requirements)
                )
                conn.commit()

                # Get the new order_id
                cursor.execute(
                    """
                    SELECT TOP 1 order_id FROM Orders
                    WHERE buyer_id = ? AND seller_id = ? AND gig_id = ?
                    ORDER BY created_at DESC
                    """,
                    (buyer_id, seller_id, gig_id)
                )
                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"OrderModel.create error: {e}")
            return None

    # ------------------------------------------------------------------
    # STATE TRANSITIONS  (State Pattern logic lives in patterns/order_state.py)
    # ------------------------------------------------------------------
    @staticmethod
    def update_status(order_id: int, status: str):
        extra = ""
        if status == "Delivered":
            extra = ", delivered_at = GETDATE()"
        elif status == "Completed":
            extra = ", completed_at = GETDATE()"

        execute_query(
            f"UPDATE Orders SET status = ?, updated_at = GETDATE(){extra} "
            f"WHERE order_id = ?",
            (status, order_id)
        )
    
        
    @staticmethod
    def set_delivery_link(order_id: int, link: str):
        execute_query(
            "UPDATE Orders SET delivery_link = ?, updated_at = GETDATE() "
            "WHERE order_id = ?",
            (link, order_id)
        )
    @staticmethod
    def delete(order_id):
        execute_query(
            "DELETE FROM Orders WHERE order_id = ?",
            (order_id,)
        )
    # ------------------------------------------------------------------
    # STATS
    # ------------------------------------------------------------------
    @staticmethod
    def count_by_seller(seller_id: int, status: str = None) -> int:
        if status:
            row = execute_query(
                "SELECT COUNT(*) AS cnt FROM Orders "
                "WHERE seller_id = ? AND status = ?",
                (seller_id, status), fetch="one"
            )
        else:
            row = execute_query(
                "SELECT COUNT(*) AS cnt FROM Orders WHERE seller_id = ?",
                (seller_id,), fetch="one"
            )
        return row["cnt"] if row else 0

    @staticmethod
    def count_by_buyer(buyer_id: int) -> int:
        row = execute_query(
            "SELECT COUNT(*) AS cnt FROM Orders WHERE buyer_id = ?",
            (buyer_id,), fetch="one"
        )
        return row["cnt"] if row else 0

    @staticmethod
    def get_seller_earnings(seller_id: int) -> float:
        row = execute_query(
            "SELECT COALESCE(SUM(amount),0) AS total FROM Orders "
            "WHERE seller_id = ? AND status = 'Completed'",
            (seller_id,), fetch="one"
        )
        return float(row["total"]) if row else 0.0

    @staticmethod
    def get_all_admin(limit: int = 50) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) o.*,
                   b.name AS buyer_name, s.name AS seller_name,
                   g.title AS gig_title
            FROM Orders o
            JOIN Users b ON b.user_id = o.buyer_id
            JOIN Users s ON s.user_id = o.seller_id
            JOIN Gigs  g ON g.gig_id  = o.gig_id
            ORDER BY o.created_at DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []