"""
Projects Controller
Routes: /post-project  /projects  /projects/<id>  /bid/<project_id>
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import login_required, current_user

from app.models.project import ProjectModel, BidModel
from app.models.order   import OrderModel
from app.models.gig     import GigModel
from app.patterns.notification_observer import (
    notify_new_bid, notify_bid_accepted
)

projects_bp = Blueprint("projects", __name__)


# ---------------------------------------------------------------
# ALL PROJECTS  /projects
# ---------------------------------------------------------------
@projects_bp.route("/projects")
@login_required
def list_projects():
    projects = ProjectModel.get_open()
    return render_template("orders/projects.html", projects=projects)


# ---------------------------------------------------------------
# POST PROJECT  /post-project
# ---------------------------------------------------------------
@projects_bp.route("/post-project", methods=["GET","POST"])
@login_required
def post_project():
    if not current_user.is_buyer():
        flash("Buyer account required.", "warning")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        title       = request.form.get("title","").strip()
        description = request.form.get("description","").strip()
        budget_min  = request.form.get("budget_min", 0, type=float)
        budget_max  = request.form.get("budget_max", 0, type=float)
        deadline    = request.form.get("deadline","")
        category    = request.form.get("category","").strip()

        if not title or not description:
            flash("Title and description are required.", "danger")
            return render_template("orders/post_project.html",
                                   form=request.form)

        project_id = ProjectModel.create(
            buyer_id    = current_user.user_id,
            title       = title,
            description = description,
            budget_min  = budget_min,
            budget_max  = budget_max,
            deadline    = deadline or None,
            category    = category,
        )
        flash("Project posted! Sellers can now bid.", "success")
        return redirect(url_for("projects.project_detail",
                                project_id=project_id))

    categories = GigModel.get_categories() or [
        "Web Development","Graphic Design","Content Writing",
        "Data Analysis","Digital Marketing","Tutoring"
    ]
    return render_template("orders/post_project.html",
                           form={}, categories=categories)


# ---------------------------------------------------------------
# PROJECT DETAIL  /projects/<project_id>
# ---------------------------------------------------------------
@projects_bp.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = ProjectModel.get_by_id(project_id)
    if not project:
        abort(404)
    bids = BidModel.get_by_project(project_id)
    already_bid = BidModel.already_bid(project_id, current_user.user_id)
    return render_template("orders/project_detail.html",
                           project=project, bids=bids,
                           already_bid=already_bid)


# ---------------------------------------------------------------
# PLACE BID  /bid/<project_id>
# ---------------------------------------------------------------
@projects_bp.route("/bid/<int:project_id>", methods=["GET","POST"])
@login_required
def place_bid(project_id):
    if not current_user.is_seller():
        flash("Seller account required to bid.", "warning")
        return redirect(url_for("projects.list_projects"))

    project = ProjectModel.get_by_id(project_id)
    if not project or project["status"] != "Open":
        flash("This project is no longer accepting bids.", "warning")
        return redirect(url_for("projects.list_projects"))

    if project["buyer_id"] == current_user.user_id:
        flash("You cannot bid on your own project.", "warning")
        return redirect(url_for("projects.project_detail",
                                project_id=project_id))

    if BidModel.already_bid(project_id, current_user.user_id):
        flash("You have already placed a bid.", "info")
        return redirect(url_for("projects.project_detail",
                                project_id=project_id))

    if request.method == "POST":
        amount        = request.form.get("amount", 0, type=float)
        delivery_days = request.form.get("delivery_days", 3, type=int)
        proposal      = request.form.get("proposal","").strip()

        if amount <= 0:
            flash("Bid amount must be greater than 0.", "danger")
            return render_template("orders/place_bid.html",
                                   project=project)

        BidModel.place(
            project_id    = project_id,
            seller_id     = current_user.user_id,
            amount        = amount,
            delivery_days = delivery_days,
            proposal      = proposal,
        )

        notify_new_bid(
            seller_name   = current_user.name,
            buyer_id      = project["buyer_id"],
            project_title = project["title"],
            project_id    = project_id,
        )
        flash("Bid placed successfully!", "success")
        return redirect(url_for("projects.project_detail",
                                project_id=project_id))

    return render_template("orders/place_bid.html", project=project)


# ---------------------------------------------------------------
# ACCEPT BID  /accept-bid/<bid_id>
# ---------------------------------------------------------------
@projects_bp.route("/accept-bid/<int:bid_id>", methods=["POST"])
@login_required
def accept_bid(bid_id):
    bid = BidModel.get_by_id(bid_id)
    if not bid:
        abort(404)

    project = ProjectModel.get_by_id(bid["project_id"])
    if project["buyer_id"] != current_user.user_id:
        abort(403)

    # Accept bid, reject others
    BidModel.accept(bid_id)
    BidModel.reject_others(bid["project_id"], bid_id)
    ProjectModel.award(bid["project_id"])

    # Create order from bid
    # Find a placeholder gig or create from bid data
    order_id = OrderModel.create(
        gig_id         = 1,           # placeholder
        buyer_id       = current_user.user_id,
        seller_id      = bid["seller_id"],
        amount         = float(bid["amount"]),
        payment_method = "coins",
        requirements   = project.get("description",""),
    )

    notify_bid_accepted(
        buyer_name = current_user.name,
        seller_id  = bid["seller_id"],
        order_id   = order_id,
    )

    flash("Bid accepted! Chat has been started.", "success")
    return redirect(url_for("chat.chat_room", order_id=order_id))