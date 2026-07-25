"""
Orders Controller
Routes: /order/<gig_id>          – place order
        /buyer-orders            – buyer order list
        /seller-orders           – seller order list
        /order-status/<order_id> – buyer views delivery
        /review/<order_id>       – leave review
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import login_required, current_user

from app.models.gig   import GigModel
from app.models.order import OrderModel
from app.models.wallet import WalletModel
from app.models.review import ReviewModel
from app.patterns.order_state      import OrderContext
from app.patterns.payment_strategy import PaymentContext
from app.patterns.notification_observer import (
    notify_new_order, notify_order_completed
)

orders_bp = Blueprint("orders", __name__)


# ---------------------------------------------------------------
# PLACE ORDER  /order/<gig_id>
# ---------------------------------------------------------------
@orders_bp.route("/order/<int:gig_id>", methods=["GET", "POST"])
@login_required
def place_order(gig_id):
    gig = GigModel.get_by_id(gig_id)
    if not gig:
        abort(404)

    # Seller can't order their own gig
    if gig["seller_id"] == current_user.user_id:
        flash("You cannot order your own gig.", "warning")
        return redirect(url_for("main.gig_detail", gig_id=gig_id))

    if not current_user.is_buyer():
        flash("You need a buyer account to place orders.", "warning")
        return redirect(url_for("main.gig_detail", gig_id=gig_id))

    balance = WalletModel.get_balance(current_user.user_id)
    balance = float(balance)

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "coins")
        requirements   = request.form.get("requirements", "").strip()

        # ── Amount based on payment method ──────────────────────
        if payment_method == "swap":
            amount = 0.0
        else:
            amount = float(gig["price"])

        # ── Validate mobile payment phone numbers ────────────────
        if payment_method == "easypaisa":
            phone = request.form.get("easypaisa_number", "").strip()
            if not phone:
                flash("Please enter your EasyPaisa phone number.", "danger")
                return render_template("orders/place_order.html",
                                    gig=gig, balance=balance)

        elif payment_method == "jazzcash":
            phone = request.form.get("jazzcash_number", "").strip()
            if not phone:
                flash("Please enter your JazzCash phone number.", "danger")
                return render_template("orders/place_order.html",
                                    gig=gig, balance=balance)

        # ── Coins balance check ──────────────────────────────────
        if payment_method == "coins" and balance < amount:
            flash(
                f"Insufficient coins. You have {balance:.0f} coins "
                f"but need {amount:.0f} coins.",
                "danger"
            )
            return render_template("orders/place_order.html",
                                gig=gig, balance=balance)

        # ── Create order record FIRST ────────────────────────────
        order_id = OrderModel.create(
            gig_id         = gig_id,
            buyer_id       = current_user.user_id,
            seller_id      = gig["seller_id"],
            amount         = amount,
            payment_method = payment_method,
            requirements   = requirements,
        )

        if not order_id:
            flash("Order could not be created. Please try again.", "danger")
            return render_template("orders/place_order.html",
                                gig=gig, balance=balance)

        # ── Strategy Pattern — process payment ───────────────────
        try:
            payment_ctx = PaymentContext(payment_method)
            result = payment_ctx.pay(
                buyer_id  = current_user.user_id,
                seller_id = gig["seller_id"],
                amount    = amount,
                order_id  = order_id,  # ✅ real order_id now
            )
        except ValueError as e:
            OrderModel.delete(order_id)
            flash(f"Invalid payment method: {str(e)}", "danger")
            return render_template("orders/place_order.html",
                                gig=gig, balance=balance)
        except Exception as e:
            OrderModel.delete(order_id)
            flash(f"Payment error: {str(e)}", "danger")
            return render_template("orders/place_order.html",
                                gig=gig, balance=balance)

        if not result.success:
            OrderModel.delete(order_id)
            flash(result.message, "danger")
            return render_template("orders/place_order.html",
                                gig=gig, balance=balance)

        # ── State Pattern — move to InProgress ───────────────────
        try:
            ctx = OrderContext(order_id=order_id, status="Pending")
            ctx.start_work()
        except Exception:
            pass

        # ── Increment gig order count ────────────────────────────
        try:
            GigModel.increment_orders(gig_id)
        except Exception:
            pass

        # ── Observer Pattern — notify seller ─────────────────────
        try:
            notify_new_order(
                buyer_name = current_user.name,
                seller_id  = gig["seller_id"],
                gig_title  = gig["title"],
                order_id   = order_id,
            )
        except Exception:
            pass

        flash("Order placed successfully! 🎉", "success")
        return redirect(url_for("chat.chat_room", order_id=order_id))

    return render_template("orders/place_order.html",
                        gig=gig, balance=balance)


# ---------------------------------------------------------------
# BUYER ORDERS  /buyer-orders
# ---------------------------------------------------------------
@orders_bp.route("/buyer-orders")
@login_required
def buyer_orders():
    orders = OrderModel.get_by_buyer(current_user.user_id)
    return render_template("orders/buyer_orders.html", orders=orders)


# ---------------------------------------------------------------
# SELLER ORDERS  /seller-orders
# ---------------------------------------------------------------
@orders_bp.route("/seller-orders")
@login_required
def seller_orders():
    if not current_user.is_seller():
        flash("Seller account required.", "warning")
        return redirect(url_for("dashboard.index"))
    orders = OrderModel.get_by_seller(current_user.user_id)
    return render_template("orders/seller_orders.html", orders=orders)


# ---------------------------------------------------------------
# ORDER STATUS  /order-status/<order_id>
# ---------------------------------------------------------------
@orders_bp.route("/order-status/<int:order_id>", methods=["GET","POST"])
@login_required
def order_status(order_id):
    order = OrderModel.get_by_id(order_id)
    if not order:
        abort(404)

    uid = current_user.user_id
    if order["buyer_id"] != uid and order["seller_id"] != uid:
        abort(403)

    is_buyer  = order["buyer_id"] == uid
    ctx       = OrderContext(order_id, order["status"],
                             order.get("delivery_link"))

    if request.method == "POST":
        action = request.form.get("action")

        # ── Seller: deliver ─────────────────────────────────────
        if action == "deliver" and order["seller_id"] == uid:
            drive_link = request.form.get("drive_link","").strip()
            if not drive_link:
                flash("Please provide a Google Drive link.", "warning")
                return redirect(url_for("orders.order_status",
                                        order_id=order_id))
            msg = ctx.deliver(drive_link)
            from app.patterns.notification_observer import notify_order_delivered
            notify_order_delivered(
                seller_name = current_user.name,
                buyer_id    = order["buyer_id"],
                order_id    = order_id,
            )
            flash(msg, "success")

        # ── Buyer: approve ──────────────────────────────────────
        elif action == "approve" and order["buyer_id"] == uid:
            msg = ctx.approve()

            # Release coins to seller (Strategy Pattern)
            if order["payment_method"] == "coins":
                payment_ctx = PaymentContext("coins")
                payment_ctx.release(
                    seller_id = order["seller_id"],
                    amount    = float(order["amount"]),
                    order_id  = order_id,
                )

            notify_order_completed(
                buyer_name = current_user.name,
                seller_id  = order["seller_id"],
                amount     = float(order["amount"]),
                order_id   = order_id,
            )
            flash(msg, "success")
            return redirect(url_for("orders.leave_review",
                                    order_id=order_id))

        # ── Cancel ──────────────────────────────────────────────
        elif action == "cancel":
            if ctx.can_cancel():
                msg = ctx.cancel()
                # Refund buyer if coins
                if order["payment_method"] == "coins":
                    payment_ctx = PaymentContext("coins")
                    payment_ctx.refund(
                        buyer_id = order["buyer_id"],
                        amount   = float(order["amount"]),
                        order_id = order_id,
                    )
                flash(msg, "info")
            else:
                flash("This order cannot be cancelled.", "warning")

        return redirect(url_for("orders.order_status",
                                order_id=order_id))

    review = ReviewModel.get_by_order(order_id)
    return render_template("orders/order_status.html",
                           order=order, ctx=ctx,
                           is_buyer=is_buyer, review=review)


# ---------------------------------------------------------------
# REVIEW  /review/<order_id>
# ---------------------------------------------------------------
@orders_bp.route("/review/<int:order_id>", methods=["GET","POST"])
@login_required
def leave_review(order_id):
    order = OrderModel.get_by_id(order_id)
    if not order:
        abort(404)
    if order["buyer_id"] != current_user.user_id:
        abort(403)
    if order["status"] != "Completed":
        flash("Order must be completed before reviewing.", "warning")
        return redirect(url_for("dashboard.index"))

    # Prevent double review
    existing = ReviewModel.get_by_order(order_id)
    if existing:
        flash("You have already reviewed this order.", "info")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        rating  = request.form.get("rating", type=int)
        comment = request.form.get("comment","").strip()

        if not rating or not (1 <= rating <= 5):
            flash("Please select a rating between 1 and 5.", "danger")
            return render_template("orders/review.html", order=order)

        ReviewModel.create(
            order_id    = order_id,
            gig_id      = order["gig_id"],
            reviewer_id = current_user.user_id,
            seller_id   = order["seller_id"],
            rating      = rating,
            comment     = comment,
        )
        flash("Review submitted! Thank you 🌟", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("orders/review.html", order=order)