"""
Profile Controller
Routes: /profile/<user_id>   public profile
        /my-profile          own profile edit
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import login_required, current_user

from app.models.user   import UserModel
from app.models.gig    import GigModel
from app.models.review import ReviewModel

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile/<int:user_id>")
def public_profile(user_id):
    user = UserModel.get_by_id(user_id)
    if not user or not user.is_active:
        abort(404)
    gigs    = GigModel.get_by_seller(user_id) if user.is_seller() else []
    reviews = ReviewModel.get_by_seller(user_id)
    return render_template("dashboard/profile.html",
                           profile_user=user,
                           gigs=gigs, reviews=reviews)


@profile_bp.route("/my-profile", methods=["GET","POST"])
@login_required
def my_profile():
    if request.method == "POST":
        name       = request.form.get("name","").strip()
        bio        = request.form.get("bio","").strip()
        university = request.form.get("university","").strip()
        country    = request.form.get("country","").strip()

        UserModel.update_profile(
            user_id    = current_user.user_id,
            name       = name or None,
            bio        = bio or None,
            university = university or None,
            country    = country or None,
        )
        flash("Profile updated!", "success")
        return redirect(url_for("profile.my_profile"))

    return render_template("dashboard/my_profile.html",
                           user=current_user)