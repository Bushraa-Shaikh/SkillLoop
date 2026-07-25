"""
Project Model – buyer posts a project; sellers place bids.
"""
from app.utils.db import execute_query


class ProjectModel:

    @staticmethod
    def get_by_id(project_id: int) -> dict:
        return execute_query(
            """
            SELECT p.*, u.name AS buyer_name,
                   u.profile_pic AS buyer_pic, u.university,
                   COUNT(b.bid_id) AS bid_count
            FROM Projects p
            JOIN Users u ON u.user_id = p.buyer_id
            LEFT JOIN Bids b ON b.project_id = p.project_id
            WHERE p.project_id = ?
            GROUP BY p.project_id, p.buyer_id, p.title, p.description,
                     p.budget_min, p.budget_max, p.deadline, p.category,
                     p.status, p.created_at,
                     u.name, u.profile_pic, u.university
            """,
            (project_id,), fetch="one"
        )

    @staticmethod
    def get_open(limit: int = 20) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) p.*, u.name AS buyer_name,
                   u.university,
                   COUNT(b.bid_id) AS bid_count
            FROM Projects p
            JOIN Users u ON u.user_id = p.buyer_id
            LEFT JOIN Bids b ON b.project_id = p.project_id
            WHERE p.status = 'Open'
            GROUP BY p.project_id, p.buyer_id, p.title, p.description,
                     p.budget_min, p.budget_max, p.deadline, p.category,
                     p.status, p.created_at,
                     u.name, u.university
            ORDER BY p.created_at DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_by_buyer(buyer_id: int) -> list:
        rows = execute_query(
            "SELECT * FROM Projects WHERE buyer_id = ? "
            "ORDER BY created_at DESC",
            (buyer_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def create(buyer_id: int, title: str, description: str,
            budget_min: float, budget_max: float,
            deadline: str, category: str) -> int:
        try:
            from app.utils.db import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO Projects
                        (buyer_id, title, description,
                        budget_min, budget_max, deadline, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (buyer_id, title, description,
                    budget_min, budget_max, deadline, category)
                )
                conn.commit()
                cursor.execute(
                    """
                    SELECT TOP 1 project_id FROM Projects
                    WHERE buyer_id = ?
                    ORDER BY created_at DESC
                    """,
                    (buyer_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"ProjectModel.create error: {e}")
            return None

    @staticmethod
    def close(project_id: int):
        execute_query(
            "UPDATE Projects SET status = 'Closed' WHERE project_id = ?",
            (project_id,)
        )

    @staticmethod
    def award(project_id: int):
        execute_query(
            "UPDATE Projects SET status = 'Awarded' WHERE project_id = ?",
            (project_id,)
        )


class BidModel:

    @staticmethod
    def get_by_id(bid_id: int) -> dict:
        return execute_query(
            """
            SELECT b.*, u.name AS seller_name,
                   u.profile_pic AS seller_pic,
                   u.rating AS seller_rating,
                   u.total_reviews AS seller_reviews,
                   u.university
            FROM Bids b
            JOIN Users u ON u.user_id = b.seller_id
            WHERE b.bid_id = ?
            """,
            (bid_id,), fetch="one"
        )

    @staticmethod
    def get_by_project(project_id: int) -> list:
        rows = execute_query(
            """
            SELECT b.*, u.name AS seller_name,
                   u.profile_pic AS seller_pic,
                   u.rating AS seller_rating,
                   u.total_reviews AS seller_reviews,
                   u.university
            FROM Bids b
            JOIN Users u ON u.user_id = b.seller_id
            WHERE b.project_id = ?
            ORDER BY b.created_at DESC
            """,
            (project_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_by_seller(seller_id: int) -> list:
        rows = execute_query(
            """
            SELECT b.*, p.title AS project_title,
                   p.status AS project_status
            FROM Bids b
            JOIN Projects p ON p.project_id = b.project_id
            WHERE b.seller_id = ?
            ORDER BY b.created_at DESC
            """,
            (seller_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def place(project_id: int, seller_id: int, amount: float,
              delivery_days: int, proposal: str) -> int:
        return execute_query(
            """
            INSERT INTO Bids
                (project_id, seller_id, amount, delivery_days, proposal)
            VALUES (?, ?, ?, ?, ?)
            """,
            (project_id, seller_id, amount, delivery_days, proposal)
        )

    @staticmethod
    def accept(bid_id: int):
        execute_query(
            "UPDATE Bids SET status = 'Accepted' WHERE bid_id = ?",
            (bid_id,)
        )

    @staticmethod
    def reject_others(project_id: int, accepted_bid_id: int):
        execute_query(
            "UPDATE Bids SET status = 'Rejected' "
            "WHERE project_id = ? AND bid_id != ?",
            (project_id, accepted_bid_id)
        )

    @staticmethod
    def already_bid(project_id: int, seller_id: int) -> bool:
        row = execute_query(
            "SELECT COUNT(*) AS cnt FROM Bids "
            "WHERE project_id = ? AND seller_id = ?",
            (project_id, seller_id), fetch="one"
        )
        return (row["cnt"] > 0) if row else False