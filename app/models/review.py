"""
Review Model – buyer reviews after order completion.
"""
from app.utils.db import execute_query


class ReviewModel:

    @staticmethod
    def get_by_gig(gig_id: int) -> list:
        rows = execute_query(
            """
            SELECT r.*, u.name AS reviewer_name,
                   u.profile_pic AS reviewer_pic,
                   u.university
            FROM Reviews r
            JOIN Users u ON u.user_id = r.reviewer_id
            WHERE r.gig_id = ?
            ORDER BY r.created_at DESC
            """,
            (gig_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_by_seller(seller_id: int) -> list:
        rows = execute_query(
            """
            SELECT r.*, u.name AS reviewer_name,
                   u.profile_pic AS reviewer_pic,
                   g.title AS gig_title
            FROM Reviews r
            JOIN Users u ON u.user_id = r.reviewer_id
            JOIN Gigs  g ON g.gig_id  = r.gig_id
            WHERE r.seller_id = ?
            ORDER BY r.created_at DESC
            """,
            (seller_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_by_order(order_id: int) -> dict:
        return execute_query(
            "SELECT * FROM Reviews WHERE order_id = ?",
            (order_id,), fetch="one"
        )

    @staticmethod
    def create(order_id: int, gig_id: int, reviewer_id: int,
               seller_id: int, rating: int, comment: str) -> int:
        review_id = execute_query(
            """
            INSERT INTO Reviews
                (order_id, gig_id, reviewer_id, seller_id, rating, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, gig_id, reviewer_id, seller_id, rating, comment)
        )
        # Update gig and seller ratings
        if review_id:
            from app.models.gig import GigModel
            from app.models.user import UserModel
            GigModel.update_rating(gig_id)
            UserModel.update_rating(seller_id)
        return review_id

    @staticmethod
    def average_for_seller(seller_id: int) -> float:
        row = execute_query(
            "SELECT AVG(CAST(rating AS FLOAT)) AS avg_r "
            "FROM Reviews WHERE seller_id = ?",
            (seller_id,), fetch="one"
        )
        return round(float(row["avg_r"]), 2) if row and row["avg_r"] else 0.0