"""
Wallet Model – coin balance + transaction history.
"""
from app.utils.db import execute_query


class WalletModel:

    @staticmethod
    def get_by_user(user_id: int) -> dict:
        return execute_query(
            "SELECT * FROM Wallet WHERE user_id = ?",
            (user_id,), fetch="one"
        )

    @staticmethod
    def get_balance(user_id: int) -> float:
        row = execute_query(
            "SELECT balance FROM Wallet WHERE user_id = ?",
            (user_id,), fetch="one"
        )
        return float(row["balance"]) if row else 0.0

    @staticmethod
    def credit(user_id: int, amount: float, description: str = "",
               order_id: int = None):
        """Add coins to wallet and record transaction."""
        execute_query(
            "UPDATE Wallet SET balance = balance + ?, updated_at = GETDATE() "
            "WHERE user_id = ?",
            (amount, user_id)
        )
        TransactionModel.record(user_id, "credit", amount,
                                description, order_id)

    @staticmethod
    def debit(user_id: int, amount: float, description: str = "",
              order_id: int = None) -> bool:
        """
        Deduct coins. Returns False if insufficient balance.
        """
        balance = WalletModel.get_balance(user_id)
        if balance < amount:
            return False
        execute_query(
            "UPDATE Wallet SET balance = balance - ?, updated_at = GETDATE() "
            "WHERE user_id = ?",
            (amount, user_id)
        )
        TransactionModel.record(user_id, "debit", amount,
                                description, order_id)
        return True

    @staticmethod
    def escrow(user_id: int, amount: float, order_id: int):
        """Hold coins in escrow when order is placed."""
        WalletModel.debit(user_id, amount,
                          f"Escrow for order #{order_id}", order_id)
        TransactionModel.record(user_id, "escrow", amount,
                                f"Escrow held for order #{order_id}", order_id)

    @staticmethod
    def release_escrow(seller_id: int, amount: float, order_id: int):
        """Release escrowed coins to seller on order completion."""
        WalletModel.credit(seller_id, amount,
                           f"Payment for order #{order_id}", order_id)
        TransactionModel.record(seller_id, "release", amount,
                                f"Escrow released for order #{order_id}",
                                order_id)


class TransactionModel:

    @staticmethod
    def record(user_id: int, txn_type: str, amount: float,
               description: str = "", order_id: int = None):
        execute_query(
            """
            INSERT INTO Transactions
                (user_id, order_id, type, amount, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, order_id, txn_type, amount, description)
        )

    @staticmethod
    def get_by_user(user_id: int, limit: int = 20) -> list:
        rows = execute_query(
            """
            SELECT TOP (?) * FROM Transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (limit, user_id), fetch="all"
        )
        return rows or []