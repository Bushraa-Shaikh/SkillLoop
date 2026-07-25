"""
Gigs Controller
Routes: /seller-gigs  /create-gig  /edit-gig/<id>  /delete-gig/<id>
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import login_required, current_user

from app.models.gig import GigModel

gigs_bp = Blueprint("gigs", __name__)


def _seller_required():
    if not current_user.is_seller():
        flash("You need a seller account to access this.", "warning")
        return redirect(url_for("dashboard.index"))
    return None


# ---------------------------------------------------------------
# SELLER GIGS  /seller-gigs
# ---------------------------------------------------------------
@gigs_bp.route("/seller-gigs")
@login_required
def seller_gigs():
    redir = _seller_required()
    if redir:
        return redir

    gigs = GigModel.get_by_seller(current_user.user_id)
    return render_template("gigs/seller_gigs.html", gigs=gigs)


# ---------------------------------------------------------------
# CREATE GIG  /create-gig
# ---------------------------------------------------------------
@gigs_bp.route("/create-gig", methods=["GET", "POST"])
@login_required
def create_gig():
    redir = _seller_required()
    if redir:
        return redir

    if request.method == "POST":
        title         = request.form.get("title", "").strip()
        description   = request.form.get("description", "").strip()
        category      = request.form.get("category", "").strip()
        price         = request.form.get("price", 0, type=float)
        delivery_days = request.form.get("delivery_days", 3, type=int)
        revisions     = request.form.get("revisions", 1, type=int)
        tags          = request.form.get("tags", "").strip()
        allow_swap    = bool(request.form.get("allow_swap"))

        # Validation
        errors = []
        if not title:
            errors.append("Title is required.")
        if not description:
            errors.append("Description is required.")
        if price < 0:
            errors.append("Price cannot be negative.")
        if delivery_days < 1:
            errors.append("Delivery days must be at least 1.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("gigs/create_gig.html",
                                   form=request.form)

        gig_id = GigModel.create(
            seller_id     = current_user.user_id,
            title         = title,
            description   = description,
            category      = category,
            price         = price,
            delivery_days = delivery_days,
            revisions     = revisions,
            tags          = tags,
            allow_swap    = allow_swap,
        )

        # Handle thumbnail upload
        thumbnail = request.files.get("thumbnail")
        if thumbnail and thumbnail.filename:
            try:
                import os
                from app.utils.helpers import save_file, allowed_file
                if allowed_file(thumbnail.filename):
                    upload_dir = os.path.join("app","static","images","gigs")
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = save_file(thumbnail, upload_dir,
                                        prefix=f"gig_{gig_id}")
                    from app.utils.db import execute_query
                    execute_query(
                        "UPDATE Gigs SET thumbnail=? WHERE gig_id=?",
                        (filename, gig_id)
                    )
            except Exception:
                pass

        flash("Gig created successfully! 🎉", "success")
        return redirect(url_for("gigs.seller_gigs"))

    categories = GigModel.get_categories() or [
        "Web Development","Mobile Development","Graphic Design",
        "UI/UX Design","Video Editing","Content Writing",
        "Data Analysis","Digital Marketing","Translation",
        "Tutoring","Music Production"
    ]
    return render_template("gigs/create_gig.html",
                           form={}, categories=categories)


# ---------------------------------------------------------------
# EDIT GIG  /edit-gig/<gig_id>
# ---------------------------------------------------------------
@gigs_bp.route("/edit-gig/<int:gig_id>", methods=["GET", "POST"])
@login_required
def edit_gig(gig_id):
    gig = GigModel.get_by_id(gig_id)
    if not gig:
        abort(404)
    if gig["seller_id"] != current_user.user_id:
        abort(403)

    if request.method == "POST":
        GigModel.update(
            gig_id        = gig_id,
            title         = request.form.get("title","").strip(),
            description   = request.form.get("description","").strip(),
            category      = request.form.get("category","").strip(),
            price         = request.form.get("price", 0, type=float),
            delivery_days = request.form.get("delivery_days",3,type=int),
            revisions     = request.form.get("revisions",1,type=int),
            tags          = request.form.get("tags","").strip(),
            allow_swap    = bool(request.form.get("allow_swap")),
        )
        flash("Gig updated successfully!", "success")
        return redirect(url_for("gigs.seller_gigs"))

    categories = GigModel.get_categories() or [
        "Web Development","Mobile Development","Graphic Design",
        "UI/UX Design","Video Editing","Content Writing",
        "Data Analysis","Digital Marketing",
    ]
    return render_template("gigs/edit_gig.html",
                           gig=gig, categories=categories)


# ---------------------------------------------------------------
# DELETE GIG  /delete-gig/<gig_id>
# ---------------------------------------------------------------
@gigs_bp.route("/delete-gig/<int:gig_id>", methods=["POST"])
@login_required
def delete_gig(gig_id):
    gig = GigModel.get_by_id(gig_id)
    if not gig:
        abort(404)
    if gig["seller_id"] != current_user.user_id:
        abort(403)
    GigModel.deactivate(gig_id)
    flash("Gig removed.", "info")
    return redirect(url_for("gigs.seller_gigs"))