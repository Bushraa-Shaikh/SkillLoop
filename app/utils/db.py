"""
Database utility – wraps pyodbc connections.
All queries go through get_db_connection() or the DBManager helper.
"""
import pyodbc
from contextlib import contextmanager
from config.config import Config
import logging

logger = logging.getLogger(__name__)


def get_connection_string() -> str:
    return Config.get_connection_string()


@contextmanager
def get_db_connection():
    """
    Context manager that yields a pyodbc connection.
    Automatically commits on success and rolls back on error.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
    """
    conn = None
    try:
        conn = pyodbc.connect(get_connection_string(), timeout=30)
        yield conn
        conn.commit()
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def execute_query(sql: str, params: tuple = (), fetch: str = None):
    """
    Execute a SQL statement and optionally fetch results.

    :param sql:    The SQL string (use ? for parameters).
    :param params: Tuple of bind parameters.
    :param fetch:  'one' | 'all' | None (for INSERT/UPDATE/DELETE)
    :return:       Row(s) as dict(s) or None.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)

        if fetch == "one":
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

        if fetch == "all":
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

        # INSERT with IDENTITY – return new id
        if sql.strip().upper().startswith("INSERT"):
            cursor.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
            result = cursor.fetchone()
            if result and result[0]:
                return int(result[0])
            return None

def execute_many(sql: str, params_list: list):
    """Execute the same statement for multiple rows."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)


def test_connection() -> bool:
    """Return True if the database is reachable."""
    try:
        with get_db_connection() as conn:
            conn.cursor().execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False