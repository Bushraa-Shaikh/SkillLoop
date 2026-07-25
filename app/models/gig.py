"""
Gig Model – wraps the Gigs and GigImages tables.
"""
from app.utils.db import execute_query


class GigModel:

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    @staticmethod
    def get_by_id(gig_id: int) -> dict:
        row = execute_query(
            """
            SELECT g.*, u.name AS seller_name, u.profile_pic AS seller_pic,
                   u.university, u.rating AS seller_rating,
                   u.total_reviews AS seller_reviews, u.country
            FROM Gigs g
            JOIN Users u ON u.user_id = g.seller_id
            WHERE g.gig_id = ? AND g.is_active = 1
            """,
            (gig_id,), fetch="one"
        )
        if row:
            row["images"] = GigModel.get_images(gig_id)
        return row

    @staticmethod
    def get_by_seller(seller_id: int) -> list:
        rows = execute_query(
            "SELECT * FROM Gigs WHERE seller_id = ? ORDER BY created_at DESC",
            (seller_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_images(gig_id: int) -> list:
        rows = execute_query(
            "SELECT * FROM GigImages WHERE gig_id = ? ORDER BY sort_order",
            (gig_id,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_featured(limit: int = 8) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) g.*, u.name AS seller_name,
                   u.university, u.profile_pic AS seller_pic
            FROM Gigs g
            JOIN Users u ON u.user_id = g.seller_id
            WHERE g.is_active = 1
            ORDER BY g.orders_count DESC, g.rating DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []

    @staticmethod
    def search(query: str = "", category: str = "",
               min_price: float = None, max_price: float = None,
               max_delivery: int = None, min_rating: float = None,
               university: str = "", sort: str = "popular") -> list:

        sql = """
            SELECT g.*, u.name AS seller_name,
                   u.university, u.profile_pic AS seller_pic
            FROM Gigs g
            JOIN Users u ON u.user_id = g.seller_id
            WHERE g.is_active = 1
        """
        params = []

        if query:
            sql += " AND (g.title LIKE ? OR g.description LIKE ? OR g.tags LIKE ?)"
            like = f"%{query}%"
            params += [like, like, like]
        if category:
            sql += " AND g.category = ?"
            params.append(category)
        if min_price is not None:
            sql += " AND g.price >= ?"
            params.append(min_price)
        if max_price is not None:
            sql += " AND g.price <= ?"
            params.append(max_price)
        if max_delivery:
            sql += " AND g.delivery_days <= ?"
            params.append(max_delivery)
        if min_rating:
            sql += " AND g.rating >= ?"
            params.append(min_rating)
        if university:
            sql += " AND u.university LIKE ?"
            params.append(f"%{university}%")

        order = {
            "popular":  "g.orders_count DESC",
            "rating":   "g.rating DESC",
            "price_low":"g.price ASC",
            "price_high":"g.price DESC",
            "newest":   "g.created_at DESC",
        }.get(sort, "g.orders_count DESC")
        sql += f" ORDER BY {order}"

        rows = execute_query(sql, tuple(params), fetch="all")
        return rows or []

    @staticmethod
    def get_by_category(category: str, limit: int = 10) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) g.*, u.name AS seller_name,
                   u.university, u.profile_pic AS seller_pic
            FROM Gigs g
            JOIN Users u ON u.user_id = g.seller_id
            WHERE g.category = ? AND g.is_active = 1
            ORDER BY g.rating DESC
            """,
            (limit, category), fetch="all"
        )
        return rows or []

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    @staticmethod
    def create(seller_id: int, title: str, description: str,
               category: str, price: float, delivery_days: int,
               revisions: int, tags: str = "",
               allow_swap: bool = False) -> int:
        gig_id = execute_query(
            """
            INSERT INTO Gigs
                (seller_id, title, description, category, price,
                 delivery_days, revisions, tags, allow_swap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (seller_id, title, description, category, price,
             delivery_days, revisions, tags, 1 if allow_swap else 0)
        )
        return gig_id

    @staticmethod
    def add_image(gig_id: int, image_path: str, sort_order: int = 0):
        execute_query(
            "INSERT INTO GigImages (gig_id, image_path, sort_order) VALUES (?,?,?)",
            (gig_id, image_path, sort_order)
        )

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    @staticmethod
    def update(gig_id: int, title: str, description: str,
               category: str, price: float, delivery_days: int,
               revisions: int, tags: str, allow_swap: bool):
        execute_query(
            """
            UPDATE Gigs SET
                title         = ?, description  = ?, category    = ?,
                price         = ?, delivery_days = ?, revisions   = ?,
                tags          = ?, allow_swap    = ?, updated_at  = GETDATE()
            WHERE gig_id = ?
            """,
            (title, description, category, price,
             delivery_days, revisions, tags,
             1 if allow_swap else 0, gig_id)
        )

    @staticmethod
    def increment_views(gig_id: int):
        execute_query(
            "UPDATE Gigs SET views = views + 1 WHERE gig_id = ?",
            (gig_id,)
        )

    @staticmethod
    def update_rating(gig_id: int):
        execute_query(
            """
            UPDATE Gigs SET
                rating       = (SELECT AVG(CAST(rating AS FLOAT))
                                FROM Reviews WHERE gig_id = ?),
                total_reviews = (SELECT COUNT(*) FROM Reviews WHERE gig_id = ?)
            WHERE gig_id = ?
            """,
            (gig_id, gig_id, gig_id)
        )

    @staticmethod
    def increment_orders(gig_id: int):
        execute_query(
            "UPDATE Gigs SET orders_count = orders_count + 1 WHERE gig_id = ?",
            (gig_id,)
        )

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    @staticmethod
    def deactivate(gig_id: int):
        execute_query(
            "UPDATE Gigs SET is_active = 0 WHERE gig_id = ?",
            (gig_id,)
        )

    @staticmethod
    def count_by_seller(seller_id: int) -> int:
        row = execute_query(
            "SELECT COUNT(*) AS cnt FROM Gigs WHERE seller_id = ? AND is_active=1",
            (seller_id,), fetch="one"
        )
        return row["cnt"] if row else 0

    @staticmethod
    def get_categories() -> list:
        rows = execute_query(
            "SELECT DISTINCT category FROM Gigs WHERE is_active=1 AND category IS NOT NULL",
            fetch="all"
        )
        return [r["category"] for r in rows] if rows else []