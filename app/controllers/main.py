"""
Main Controller – public-facing routes
Routes: / (homepage), /browse, /gig/<id>
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from flask_login import current_user

from app.models.gig  import GigModel
from app.models.user import UserModel

main_bp = Blueprint("main", __name__)


# ---------------------------------------------------------------
# HOME  /
# ---------------------------------------------------------------
@main_bp.route("/")
def index():
    featured       = GigModel.get_featured(limit=8)
    top_performers = UserModel.get_top_performers(limit=6)
    new_talent     = UserModel.get_new_talent(limit=6)
    rising_stars   = UserModel.get_rising_stars(limit=6)
    categories     = GigModel.get_categories()

    return render_template(
        "index.html",
        featured       = featured,
        top_performers = top_performers,
        new_talent     = new_talent,
        rising_stars   = rising_stars,
        categories     = categories,
    )


# ---------------------------------------------------------------
# BROWSE  /browse
# ---------------------------------------------------------------
@main_bp.route("/browse")
def browse():
    query       = request.args.get("q", "")
    category    = request.args.get("category", "")
    min_price   = request.args.get("min_price", type=float)
    max_price   = request.args.get("max_price", type=float)
    max_delivery= request.args.get("delivery", type=int)
    min_rating  = request.args.get("rating", type=float)
    university  = request.args.get("university", "")
    sort        = request.args.get("sort", "popular")
    page        = request.args.get("page", 1, type=int)

    gigs = GigModel.search(
        query        = query,
        category     = category,
        min_price    = min_price,
        max_price    = max_price,
        max_delivery = max_delivery,
        min_rating   = min_rating,
        university   = university,
        sort         = sort,
    )

    # Paginate
    per_page    = 12
    total       = len(gigs)
    start       = (page - 1) * per_page
    gigs_page   = gigs[start: start + per_page]
    total_pages = (total + per_page - 1) // per_page

    categories = GigModel.get_categories()

    return render_template(
        "gigs/browse.html",
        gigs        = gigs_page,
        total       = total,
        page        = page,
        total_pages = total_pages,
        categories  = categories,
        filters     = {
            "q": query, "category": category,
            "min_price": min_price, "max_price": max_price,
            "delivery": max_delivery, "rating": min_rating,
            "university": university, "sort": sort,
        },
    )


# ---------------------------------------------------------------
# GIG DETAIL  /gig/<gig_id>
# ---------------------------------------------------------------
@main_bp.route("/gig/<int:gig_id>")
def gig_detail(gig_id):
    gig = GigModel.get_by_id(gig_id)
    if not gig:
        flash("Gig not found.", "danger")
        return redirect(url_for("main.browse"))

    # Increment view count
    GigModel.increment_views(gig_id)

    from app.models.review import ReviewModel
    reviews = ReviewModel.get_by_gig(gig_id)

    # Check if current user already ordered this gig
    already_ordered = False
    if current_user.is_authenticated:
        from app.models.order import OrderModel
        orders = OrderModel.get_by_buyer(current_user.user_id)
        already_ordered = any(
            o["gig_id"] == gig_id and
            o["status"] not in ("Cancelled",)
            for o in orders
        )

    return render_template(
        "gigs/gig_detail.html",
        gig            = gig,
        reviews        = reviews,
        already_ordered= already_ordered,
    )