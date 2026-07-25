"""
Dashboard Controller – role-based main dashboard
Route: /dashboard
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.order        import OrderModel
from app.models.gig          import GigModel
from app.models.notification import NotificationModel
from app.models.message      import MessageModel
from app.models.wallet       import WalletModel

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    uid = current_user.user_id

    # Common data for all roles
    notifications  = NotificationModel.get_by_user(uid, limit=5)
    unread_notifs  = NotificationModel.unread_count(uid)
    unread_msgs    = MessageModel.unread_count(uid)
    wallet_balance = WalletModel.get_balance(uid)

    context = dict(
        notifications  = notifications,
        unread_notifs  = unread_notifs,
        unread_msgs    = unread_msgs,
        wallet_balance = wallet_balance,
    )

    # ── BUYER data ─────────────────────────────────────────────
    if current_user.is_buyer():
        buyer_orders = OrderModel.get_by_buyer(uid)
        context["buyer_orders"]       = buyer_orders[:5]
        context["total_buyer_orders"] = len(buyer_orders)
        context["active_orders"]      = [
            o for o in buyer_orders
            if o["status"] in ("Pending","InProgress","Delivered")
        ]

    # ── SELLER data ────────────────────────────────────────────
    if current_user.is_seller():
        seller_orders  = OrderModel.get_active_by_seller(uid)
        seller_gigs    = GigModel.get_by_seller(uid)
        total_earnings = OrderModel.get_seller_earnings(uid)
        completed      = OrderModel.count_by_seller(uid, "Completed")

        context["seller_orders"]   = seller_orders[:5]
        context["seller_gigs"]     = seller_gigs[:4]
        context["total_gigs"]      = len(seller_gigs)
        context["total_earnings"]  = total_earnings
        context["completed_orders"]= completed

    return render_template("dashboard/dashboard.html", **context)


# ---------------------------------------------------------------
# Notifications  /notifications
# ---------------------------------------------------------------
@dashboard_bp.route("/notifications")
@login_required
def notifications():
    uid    = current_user.user_id
    notifs = NotificationModel.get_by_user(uid, limit=50)
    NotificationModel.mark_all_read(uid)
    return render_template("dashboard/notifications.html",
                           notifications=notifs)