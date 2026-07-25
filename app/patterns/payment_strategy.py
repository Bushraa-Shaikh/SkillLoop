"""
STRATEGY DESIGN PATTERN
========================
Problem : SkillLoop supports four payment methods:
            1. Campus Coins  – deduct from buyer's wallet
            2. Skill Swap    – exchange services, no coins
            3. EasyPaisa     – mobile wallet payment
            4. JazzCash      – mobile wallet payment
          The order placement logic must not care which method is used.
Solution: Define a PaymentStrategy interface. Each method is a
          concrete strategy. The PaymentContext selects and runs it.

Strategy Interface : PaymentStrategy
Concrete Strategies: CampusCoinsStrategy, SkillSwapStrategy,
                     EasyPaisaStrategy, JazzCashStrategy
Context            : PaymentContext
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------
# RESULT  – standardised return from every strategy
# ---------------------------------------------------------------
@dataclass
class PaymentResult:
    success:     bool
    method:      str
    amount:      float
    message:     str
    transaction_id: int = None

    def to_dict(self) -> dict:
        return {
            "success":        self.success,
            "method":         self.method,
            "amount":         self.amount,
            "message":        self.message,
            "transaction_id": self.transaction_id,
        }


# ---------------------------------------------------------------
# ABSTRACT STRATEGY
# ---------------------------------------------------------------
class PaymentStrategy(ABC):

    @abstractmethod
    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        pass

    @abstractmethod
    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        pass

    @abstractmethod
    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        pass


# ---------------------------------------------------------------
# CONCRETE STRATEGY 1 – Campus Coins
# ---------------------------------------------------------------
class CampusCoinsStrategy(PaymentStrategy):

    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import WalletModel
            balance = WalletModel.get_balance(buyer_id)
            if balance < amount:
                return PaymentResult(
                    success=False, method="coins",
                    amount=amount,
                    message=f"Insufficient coins. "
                            f"Balance: {balance:.0f}, Required: {amount:.0f}"
                )
            WalletModel.debit(
                buyer_id, amount,
                f"Payment for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="coins",
                amount=amount,
                message=f"{amount:.0f} coins deducted. Held in escrow."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="coins",
                amount=amount, message=str(e)
            )

    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import WalletModel
            WalletModel.credit(
                buyer_id, amount,
                f"Refund for cancelled order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="coins",
                amount=amount,
                message=f"{amount:.0f} coins refunded to your wallet."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="coins",
                amount=amount, message=str(e)
            )

    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import WalletModel
            WalletModel.release_escrow(seller_id, amount, order_id)
            return PaymentResult(
                success=True, method="coins",
                amount=amount,
                message=f"{amount:.0f} coins released to your wallet!"
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="coins",
                amount=amount, message=str(e)
            )

    def get_method_name(self) -> str:
        return "coins"


# ---------------------------------------------------------------
# CONCRETE STRATEGY 2 – Skill Swap
# ---------------------------------------------------------------
class SkillSwapStrategy(PaymentStrategy):

    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import TransactionModel
            TransactionModel.record(
                buyer_id, "swap", 0,
                f"Skill Swap initiated for order #{order_id}", order_id
            )
            TransactionModel.record(
                seller_id, "swap", 0,
                f"Skill Swap accepted for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="swap",
                amount=0,
                message="Skill Swap agreed! No coins deducted."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="swap",
                amount=0, message=str(e)
            )

    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        return PaymentResult(
            success=True, method="swap", amount=0,
            message="Skill Swap cancelled. No refund needed."
        )

    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        return PaymentResult(
            success=True, method="swap", amount=0,
            message="Skill Swap completed successfully!"
        )

    def get_method_name(self) -> str:
        return "swap"


# ---------------------------------------------------------------
# CONCRETE STRATEGY 3 – EasyPaisa
# ---------------------------------------------------------------
class EasyPaisaStrategy(PaymentStrategy):

    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import TransactionModel
            TransactionModel.record(
                buyer_id, "easypaisa", amount,
                f"EasyPaisa payment for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="easypaisa",
                amount=amount,
                message=f"EasyPaisa payment of Rs.{amount:.0f} recorded successfully."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="easypaisa",
                amount=amount, message=str(e)
            )

    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import TransactionModel
            TransactionModel.record(
                buyer_id, "refund", amount,
                f"EasyPaisa refund for cancelled order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="easypaisa",
                amount=amount,
                message=f"EasyPaisa refund of Rs.{amount:.0f} will be processed in 3-5 days."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="easypaisa",
                amount=amount, message=str(e)
            )

    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import WalletModel
            WalletModel.credit(
                seller_id, amount,
                f"EasyPaisa payment received for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="easypaisa",
                amount=amount,
                message=f"Rs.{amount:.0f} payment confirmed. Coins added to your wallet."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="easypaisa",
                amount=amount, message=str(e)
            )

    def get_method_name(self) -> str:
        return "easypaisa"


# ---------------------------------------------------------------
# CONCRETE STRATEGY 4 – JazzCash
# ---------------------------------------------------------------
class JazzCashStrategy(PaymentStrategy):

    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import TransactionModel
            TransactionModel.record(
                buyer_id, "jazzcash", amount,
                f"JazzCash payment for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="jazzcash",
                amount=amount,
                message=f"JazzCash payment of Rs.{amount:.0f} recorded successfully."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="jazzcash",
                amount=amount, message=str(e)
            )

    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import TransactionModel
            TransactionModel.record(
                buyer_id, "refund", amount,
                f"JazzCash refund for cancelled order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="jazzcash",
                amount=amount,
                message=f"JazzCash refund of Rs.{amount:.0f} will be processed in 3-5 days."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="jazzcash",
                amount=amount, message=str(e)
            )

    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        try:
            from app.models.wallet import WalletModel
            WalletModel.credit(
                seller_id, amount,
                f"JazzCash payment received for order #{order_id}", order_id
            )
            return PaymentResult(
                success=True, method="jazzcash",
                amount=amount,
                message=f"Rs.{amount:.0f} payment confirmed. Coins added to your wallet."
            )
        except Exception as e:
            return PaymentResult(
                success=False, method="jazzcash",
                amount=amount, message=str(e)
            )

    def get_method_name(self) -> str:
        return "jazzcash"


# ---------------------------------------------------------------
# CONTEXT  – selects and executes the right strategy
# ---------------------------------------------------------------
class PaymentContext:

    _strategies = {
        "coins":     CampusCoinsStrategy,
        "swap":      SkillSwapStrategy,
        "easypaisa": EasyPaisaStrategy,   # ✅ added
        "jazzcash":  JazzCashStrategy,    # ✅ added
    }

    def __init__(self, method: str = "coins"):
        cls = self._strategies.get(method)
        if not cls:
            raise ValueError(
                f"Unknown payment method '{method}'. "
                f"Valid: {list(self._strategies.keys())}"
            )
        self._strategy: PaymentStrategy = cls()

    def pay(self, buyer_id: int, seller_id: int,
            amount: float, order_id: int) -> PaymentResult:
        return self._strategy.pay(buyer_id, seller_id, amount, order_id)

    def refund(self, buyer_id: int, amount: float,
               order_id: int) -> PaymentResult:
        return self._strategy.refund(buyer_id, amount, order_id)

    def release(self, seller_id: int, amount: float,
                order_id: int) -> PaymentResult:
        return self._strategy.release(seller_id, amount, order_id)

    def get_method_name(self) -> str:
        return self._strategy.get_method_name()

    @staticmethod
    def valid_methods() -> list:
        return list(PaymentContext._strategies.keys())