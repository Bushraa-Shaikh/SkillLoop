"""
Wallet Controller
Route: /wallet
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.wallet import WalletModel, TransactionModel

wallet_bp = Blueprint("wallet", __name__)

@wallet_bp.route("/wallet")
@login_required
def wallet():
    balance      = WalletModel.get_balance(current_user.user_id)
    transactions = TransactionModel.get_by_user(
                       current_user.user_id, limit=30)
    return render_template("dashboard/wallet.html",
                           balance=balance,
                           transactions=transactions)