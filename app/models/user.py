"""
User Model – wraps the Users table.
Implements Flask-Login's UserMixin for session management.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import execute_query
from datetime import datetime


class User(UserMixin):
    """
    Flask-Login compatible User object.
    Built from a database row dict.
    """
    def __init__(self, data: dict):
        self.id                  = data.get("user_id")
        self.user_id             = data.get("user_id")
        self.name                = data.get("name")
        self.email               = data.get("email")
        self.password_hash       = data.get("password_hash")
        self.university          = data.get("university")
        self.country             = data.get("country")
        self.bio                 = data.get("bio")
        self.profile_pic         = data.get("profile_pic")
        self.role                = data.get("role", "buyer")
        self.is_verified         = bool(data.get("is_verified", False))
        self.verification_method = data.get("verification_method")
        self.auth_provider       = data.get("auth_provider", "local")
        self.google_id           = data.get("google_id")
        self._is_active          = bool(data.get("is_active", True))
        self.joined_at           = data.get("joined_at")
        self.last_login          = data.get("last_login")
        self.rating              = data.get("rating", 0)
        self.total_reviews       = data.get("total_reviews", 0)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self._is_active

    def is_seller(self) -> bool:
        return self.role in ("seller", "both")

    def is_buyer(self) -> bool:
        return self.role in ("buyer", "both")

    def is_admin(self) -> bool:
        return self.role == "admin"

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.user_id} {self.email}>"


class UserModel:
    """
    Data Access Object for the Users table.
    All DB operations for users live here.
    """

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------
    @staticmethod
    def get_by_id(user_id: int):
        row = execute_query(
            "SELECT * FROM Users WHERE user_id = ?",
            (user_id,), fetch="one"
        )
        return User(row) if row else None

    @staticmethod
    def get_by_email(email: str):
        row = execute_query(
            "SELECT * FROM Users WHERE email = ?",
            (email,), fetch="one"
        )
        return User(row) if row else None

    @staticmethod
    def get_by_google_id(google_id: str):
        row = execute_query(
            "SELECT * FROM Users WHERE google_id = ?",
            (google_id,), fetch="one"
        )
        return User(row) if row else None

    @staticmethod
    def get_all(limit: int = 50, offset: int = 0):
        rows = execute_query(
            "SELECT * FROM Users ORDER BY joined_at DESC "
            "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY",
            (offset, limit), fetch="all"
        )
        return [User(r) for r in rows] if rows else []

    @staticmethod
    def search(query: str):
        like = f"%{query}%"
        rows = execute_query(
            "SELECT * FROM Users WHERE name LIKE ? OR university LIKE ?",
            (like, like), fetch="all"
        )
        return [User(r) for r in rows] if rows else []

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    @staticmethod
    def create(name: str, email: str, password: str,
            university: str = None, country: str = None,
            auth_provider: str = "local", google_id: str = None) -> int:
        """
        Insert a new user and return the new user_id.
        Also creates a wallet entry for the user.
        """
        from werkzeug.security import generate_password_hash
        pw_hash = generate_password_hash(password) if password else None

        try:
            from app.utils.db import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert user
                cursor.execute(
                    """
                    INSERT INTO Users
                        (name, email, password_hash, university, country,
                        auth_provider, google_id, role, is_verified, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'buyer', 0, 1)
                    """,
                    (name, email, pw_hash, university, country,
                    auth_provider, google_id)
                )
                conn.commit()

                # Get the new user_id
                cursor.execute(
                    "SELECT user_id FROM Users WHERE email = ?", (email,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                user_id = row[0]

                # Create wallet
                cursor.execute(
                    "SELECT wallet_id FROM Wallet WHERE user_id = ?", (user_id,)
                )
                if not cursor.fetchone():
                    from config.config import Config
                    cursor.execute(
                        "INSERT INTO Wallet (user_id, balance) VALUES (?, ?)",
                        (user_id, Config.INITIAL_COINS)
                    )
                    conn.commit()

                return user_id

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"UserModel.create error: {e}")
            return None

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    @staticmethod
    def update_profile(user_id: int, name: str = None, bio: str = None,
                       university: str = None, country: str = None,
                       profile_pic: str = None):
        execute_query(
            """
            UPDATE Users SET
                name        = COALESCE(?, name),
                bio         = COALESCE(?, bio),
                university  = COALESCE(?, university),
                country     = COALESCE(?, country),
                profile_pic = COALESCE(?, profile_pic)
            WHERE user_id = ?
            """,
            (name, bio, university, country, profile_pic, user_id)
        )

    @staticmethod
    def update_role(user_id: int, role: str):
        execute_query(
            "UPDATE Users SET role = ? WHERE user_id = ?",
            (role, user_id)
        )

    @staticmethod
    def verify_user(user_id: int, method: str):
        execute_query(
            "UPDATE Users SET is_verified = 1, verification_method = ? "
            "WHERE user_id = ?",
            (method, user_id)
        )

    @staticmethod
    def update_last_login(user_id: int):
        execute_query(
            "UPDATE Users SET last_login = GETDATE() WHERE user_id = ?",
            (user_id,)
        )

    @staticmethod
    def update_password(user_id: int, new_password: str):
        pw_hash = generate_password_hash(new_password)
        execute_query(
            "UPDATE Users SET password_hash = ? WHERE user_id = ?",
            (pw_hash, user_id)
        )

    @staticmethod
    def update_rating(user_id: int):
        """Recalculate and store seller rating from Reviews table."""
        execute_query(
            """
            UPDATE Users SET
                rating       = (SELECT AVG(CAST(rating AS FLOAT))
                                FROM Reviews WHERE seller_id = ?),
                total_reviews = (SELECT COUNT(*) FROM Reviews WHERE seller_id = ?)
            WHERE user_id = ?
            """,
            (user_id, user_id, user_id)
        )

    # ------------------------------------------------------------------
    # DELETE / DEACTIVATE
    # ------------------------------------------------------------------
    @staticmethod
    def deactivate(user_id: int):
        execute_query(
            "UPDATE Users SET is_active = 0 WHERE user_id = ?",
            (user_id,)
        )

    # ------------------------------------------------------------------
    # STATS / DISCOVERY
    # ------------------------------------------------------------------
    @staticmethod
    def get_top_performers(limit: int = 6):
        rows = execute_query(
            """
            SELECT TOP (?) 
                u.user_id, u.name, u.email, u.university,
                u.country, u.bio, u.profile_pic, u.role,
                u.is_verified, u.auth_provider, u.is_active,
                u.joined_at, u.last_login, u.rating,
                u.total_reviews,
                COUNT(o.order_id) AS completed_orders
            FROM Users u
            LEFT JOIN Orders o ON o.seller_id = u.user_id
                            AND o.status = 'Completed'
            WHERE u.role IN ('seller','both') AND u.is_active = 1
            GROUP BY u.user_id, u.name, u.email, u.university,
                    u.country, u.bio, u.profile_pic, u.role,
                    u.is_verified, u.auth_provider, u.is_active,
                    u.joined_at, u.last_login, u.rating,
                    u.total_reviews
            ORDER BY u.rating DESC, completed_orders DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_new_talent(limit: int = 6):
        rows = execute_query(
            """
            SELECT TOP (?)
                user_id, name, email, university, country,
                bio, profile_pic, role, is_verified,
                auth_provider, is_active, joined_at,
                last_login, rating, total_reviews
            FROM Users
            WHERE role IN ('seller','both')
            AND is_active = 1
            AND joined_at >= DATEADD(DAY, -30, GETDATE())
            ORDER BY joined_at DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []

    @staticmethod
    def get_rising_stars(limit: int = 6):
        rows = execute_query(
            """
            SELECT TOP (?)
                user_id, name, email, university, country,
                bio, profile_pic, role, is_verified,
                auth_provider, is_active, joined_at,
                last_login, rating, total_reviews
            FROM Users
            WHERE role IN ('seller','both')
            AND is_active = 1
            AND rating >= 4.5
            AND total_reviews >= 3
            ORDER BY total_reviews DESC, rating DESC
            """,
            (limit,), fetch="all"
        )
        return rows or []

    @staticmethod
    def count_all() -> int:
        row = execute_query("SELECT COUNT(*) AS cnt FROM Users", fetch="one")
        return row["cnt"] if row else 0