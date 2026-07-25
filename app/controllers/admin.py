"""
Admin Controller
Route: /admin  (all routes prefixed with /admin)
"""
from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, abort)
from flask_login import login_required, current_user

from app.models.user   import UserModel
from app.models.gig    import GigModel
from app.models.order  import OrderModel
from app.utils.db      import execute_query

admin_bp = Blueprint("admin", __name__)


def _admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)


# ---------------------------------------------------------------
# ADMIN DASHBOARD  /admin/
# ---------------------------------------------------------------
@admin_bp.route("/")
@login_required
def index():
    _admin_required()
    total_users  = UserModel.count_all()
    try:
        total_gigs   = execute_query(
            "SELECT COUNT(*) AS cnt FROM Gigs WHERE is_active=1",
            fetch="one")["cnt"]
        total_orders = execute_query(
            "SELECT COUNT(*) AS cnt FROM Orders",
            fetch="one")["cnt"]
        total_revenue= execute_query(
            "SELECT COALESCE(SUM(amount),0) AS total FROM Orders "
            "WHERE status='Completed'",
            fetch="one")["total"]
    except Exception:
        total_gigs = total_orders = total_revenue = 0

    recent_orders = OrderModel.get_all_admin(limit=10)
    return render_template(
        "admin/dashboard.html",
        total_users   = total_users,
        total_gigs    = total_gigs,
        total_orders  = total_orders,
        total_revenue = total_revenue,
        recent_orders = recent_orders,
    )


# ---------------------------------------------------------------
# ADMIN USERS  /admin/users
# ---------------------------------------------------------------
@admin_bp.route("/users")
@login_required
def users():
    _admin_required()
    all_users = UserModel.get_all(limit=100)
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id):
    _admin_required()
    UserModel.deactivate(user_id)
    flash("User deactivated.", "info")
    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------
# ADMIN GIGS  /admin/gigs
# ---------------------------------------------------------------
@admin_bp.route("/gigs")
@login_required
def gigs():
    _admin_required()
    try:
        all_gigs = execute_query(
            """
            SELECT g.*, u.name AS seller_name
            FROM Gigs g JOIN Users u ON u.user_id=g.seller_id
            ORDER BY g.created_at DESC
            """, fetch="all") or []
    except Exception:
        all_gigs = []
    return render_template("admin/gigs.html", gigs=all_gigs)


@admin_bp.route("/gigs/<int:gig_id>/remove", methods=["POST"])
@login_required
def remove_gig(gig_id):
    _admin_required()
    GigModel.deactivate(gig_id)
    flash("Gig removed.", "info")
    return redirect(url_for("admin.gigs"))


# ---------------------------------------------------------------
# ADMIN ORDERS  /admin/orders
# ---------------------------------------------------------------
@admin_bp.route("/orders")
@login_required
def orders():
    _admin_required()
    all_orders = OrderModel.get_all_admin(limit=100)
    return render_template("admin/orders.html", orders=all_orders)