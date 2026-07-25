"""
Auth Controller
Routes: /login  /signup  /logout
        /auth/google  /auth/google/callback
        /verify-student  /profile-setup
"""
import os
import secrets
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from flask_login import (login_user, logout_user,
                         login_required, current_user)

from app.models.user              import UserModel
from app.models.wallet            import WalletModel
from app.patterns.user_factory    import UserFactory
from app.patterns.google_auth_adapter import get_auth_adapter
from app.utils.helpers            import (is_valid_email, is_student_email,
                                          validate_password)
from config.config                import Config

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------
# helpers
# ---------------------------------------------------------------
def _login_and_redirect(user, next_page=None):
    """Log user in and redirect appropriately."""
    login_user(user, remember=True)
    UserModel.update_last_login(user.user_id)
    if not user.is_verified:
        return redirect(url_for("auth.verify_student"))
    target = next_page or url_for("dashboard.index")
    return redirect(target)


# ---------------------------------------------------------------
# SIGNUP  /signup
# ---------------------------------------------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect (url_for("dashboard.index"))

    if request.method == "POST":
        name       = request.form.get("name", "").strip()
        email      = request.form.get("email", "").strip().lower()
        password   = request.form.get("password", "")
        confirm    = request.form.get("confirm_password", "")
        university = request.form.get("university", "").strip()
        country    = request.form.get("country", "").strip()

        # ── Validation ──────────────────────────────────────────
        errors = []

        if not name:
            errors.append("Name is required.")

        if not is_valid_email(email):
            errors.append("Enter a valid email address.")
        
        if not is_student_email(email):
            errors.append(
                "Only educational email addresses are accepted. "
                "Please use your university email "
                "(e.g. name@university.edu.pk)"
            )

        try:
            existing = UserModel.get_by_email(email)
            if existing:
                errors.append("An account with this email already exists.")
        except Exception:
            pass

        valid_pw, pw_msg = validate_password(password)
        if not valid_pw:
            errors.append(pw_msg)

        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("auth/signup.html", form=request.form)

        # ── Create user ──────────────────────────────────────────
        try:
            user_id = UserModel.create(
                name=name,
                email=email,
                password=password,
                university=university,
                country=country,
            )
        except Exception as e:
            flash(f"Registration error: {str(e)}", "danger")
            return render_template("auth/signup.html", form=request.form)

        if not user_id:
            flash("Account creation failed. Please try again.", "danger")
            return render_template("auth/signup.html", form=request.form)

        try:
            user = UserModel.get_by_id(user_id)
        except Exception:
            user = None

        if not user:
            flash("Account created but login failed. Please login manually.", "warning")
            return redirect(url_for("auth.login"))

        # Store user_id in session but DON'T login yet
        from flask import session
        session['pending_user_id'] = user_id
        flash("Account created! Please verify your email.", "success")
        return redirect(url_for("auth.verify_student"))

    # GET request
    return render_template("auth/signup.html", form={})

# ---------------------------------------------------------------
# LOGIN  /login
# ---------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = UserModel.get_by_email(email)

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", email=email)

# Google-only account — has no password
        if getattr(user, 'auth_provider', None) == "google" and not getattr(user, 'password_hash', None):
            flash(
                "This account uses Google sign-in. "
                "Please click 'Sign in with Google' instead.",
                "warning"
            )
            return render_template("auth/login.html", email=email)
        
        if not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", email=email)


        if not user.is_active:
            flash("Your account has been deactivated.", "warning")
            return render_template("auth/login.html")

        return _login_and_redirect(user)

    return render_template("auth/login.html", email="")


# ---------------------------------------------------------------
# LOGOUT  /logout
# ---------------------------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------
# GOOGLE AUTH  /auth/google
# ---------------------------------------------------------------
@auth_bp.route("/auth/google")
def google_login():
    adapter   = get_auth_adapter(
        "google",
        client_id     = Config.GOOGLE_CLIENT_ID,
        client_secret = Config.GOOGLE_CLIENT_SECRET,
        redirect_uri  = Config.GOOGLE_REDIRECT_URI,
    )
    state     = secrets.token_hex(16)
    session["oauth_state"] = state
    auth_url  = adapter.get_auth_url(state=state)
    return redirect(auth_url)


# ---------------------------------------------------------------
# GOOGLE CALLBACK  /auth/google/callback
# ---------------------------------------------------------------
@auth_bp.route("/auth/google/callback")
def google_callback():
    code  = request.args.get("code")
    state = request.args.get("state")

    if not code:
        flash("Google login failed. No code received.", "danger")
        return redirect(url_for("auth.login"))

    if state != session.get("oauth_state"):
        flash("Invalid state parameter. Possible CSRF.", "danger")
        return redirect(url_for("auth.login"))

    try:
        adapter = get_auth_adapter(
            "google",
            client_id     = Config.GOOGLE_CLIENT_ID,
            client_secret = Config.GOOGLE_CLIENT_SECRET,
            redirect_uri  = Config.GOOGLE_REDIRECT_URI,
        )
        tokens    = adapter.exchange_code(code)
        user_info = adapter.get_user_info(tokens["access_token"])

    except Exception as e:
        flash(f"Google authentication error: {str(e)}", "danger")
        return redirect(url_for("auth.login"))

    email       = user_info.get("email")
    name        = user_info.get("name")
    provider_id = user_info.get("provider_id")

    if not email:
        flash("Could not retrieve email from Google.", "danger")
        return redirect(url_for("auth.login"))

    # Block non-educational emails
    if not is_student_email(email):
        flash(
            "Only educational email addresses are accepted. "
            "Please use your university Google account "
            "(e.g. name@university.edu.pk).",
            "danger"
        )
        return redirect(url_for("auth.login"))


    user = UserModel.get_by_email(email)

    if user:
        # Existing user – log in
        return _login_and_redirect(user)
    else:
        # New user – create account
        user_id = UserModel.create(
            name          = name,
            email         = email,
            password      = None,
            auth_provider = "google",
            google_id     = provider_id,
        )
        user = UserModel.get_by_id(user_id)
        login_user(user, remember=True)
        flash("Account created via Google! Please verify.", "success")
        return redirect(url_for("auth.verify_student"))


# ---------------------------------------------------------------
# VERIFY STUDENT  /verify-student
# ---------------------------------------------------------------
@auth_bp.route("/verify-student", methods=["GET", "POST"])
def verify_student():
    from flask import session
    from app.utils.db import execute_query
    import random
    from datetime import datetime, timedelta

    # Get user — either logged in or pending
    uid = None
    if current_user.is_authenticated:
        if current_user.is_verified:
            return redirect(url_for("auth.profile_setup"))
        uid = current_user.user_id
    elif session.get('pending_user_id'):
        uid = session['pending_user_id']
    else:
        flash("Please sign up first.", "warning")
        return redirect(url_for("auth.signup"))

    # Get user object
    user = UserModel.get_by_id(uid)
    if not user:
        flash("User not found. Please sign up again.", "danger")
        return redirect(url_for("auth.signup"))

    if request.method == "POST":
        action = request.form.get("action", "")

        # ── Send OTP ─────────────────────────────────────────
        if action == "send_otp":
            otp    = str(random.randint(100000, 999999))
            expiry = datetime.now() + timedelta(minutes=10)

            execute_query(
                "UPDATE Users SET otp_code=?, otp_expiry=? WHERE user_id=?",
                (otp, expiry, uid)
            )

            # Try sending real email
            email_sent = False
            try:
                from flask_mail import Message
                from app import mail
                from flask import current_app
                if current_app.config.get("MAIL_USERNAME"):
                    msg = Message(
                        subject    = "SkillLoop — Your Verification Code",
                        sender     = current_app.config["MAIL_USERNAME"],
                        recipients = [user.email]
                    )
                    msg.body = (
                        f"Hi {user.name},\n\n"
                        f"Your SkillLoop verification code is:\n\n"
                        f"        {otp}\n\n"
                        f"This code expires in 10 minutes.\n"
                        f"Do not share this code with anyone.\n\n"
                        f"— SkillLoop Team"
                    )
                    mail.send(msg)
                    email_sent = True
                    flash(
                        f"Verification code sent to {user.email}! "
                        f"Check your inbox and spam folder.",
                        "success"
                    )
            except Exception as e:
                pass

            if not email_sent:
                # Development mode — show OTP on screen
                flash(
                    f"Dev Mode — Email not configured. Your OTP is: {otp}",
                    "info"
                )

            return render_template(
                "auth/verify_student.html",
                show_otp_input=True,
                auto_verified=False,
                user_email=user.email,
            )

        # ── Verify OTP ───────────────────────────────────────
        elif action == "verify_otp":
            entered = request.form.get("otp", "").strip()

            row = execute_query(
                "SELECT otp_code, otp_expiry FROM Users WHERE user_id=?",
                (uid,), fetch="one"
            )

            if not row or not row["otp_code"]:
                flash("No code found. Please request a new one.", "danger")
                return render_template("auth/verify_student.html",
                    show_otp_input=False, auto_verified=False,
                    user_email=user.email)

            expiry = row["otp_expiry"]
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S.%f")
            if datetime.now() > expiry:
                flash("Code expired. Please request a new one.", "danger")
                return render_template("auth/verify_student.html",
                    show_otp_input=False, auto_verified=False,
                    user_email=user.email)

            if entered != row["otp_code"]:
                flash("Wrong code. Please try again.", "danger")
                return render_template("auth/verify_student.html",
                    show_otp_input=True, auto_verified=False,
                    user_email=user.email)

            # ✅ OTP correct — verify and login
            UserModel.verify_user(uid, "otp")
            execute_query(
                "UPDATE Users SET otp_code=NULL, otp_expiry=NULL WHERE user_id=?",
                (uid,)
            )
            session.pop('pending_user_id', None)

            # Now actually login
            verified_user = UserModel.get_by_id(uid)
            login_user(verified_user, remember=True)
            UserModel.update_last_login(uid)

            flash("Email verified! Welcome to SkillLoop! 🎉", "success")
            return redirect(url_for("auth.profile_setup"))

    return render_template(
        "auth/verify_student.html",
        show_otp_input=False,
        auto_verified=False,
        user_email=user.email,
        user=user,
    )


    # ── OPTION 4: OTP for non-educational emails ─────────────────
    from app.utils.db import execute_query
    import random
    from datetime import datetime, timedelta

    if request.method == "POST":
        action = request.form.get("action", "")

        # ── Send OTP ─────────────────────────────────────────────
        if action == "send_otp":
            otp    = str(random.randint(100000, 999999))
            expiry = datetime.now() + timedelta(minutes=10)

            execute_query(
                "UPDATE Users SET otp_code=?, otp_expiry=? "
                "WHERE user_id=?",
                (otp, expiry, current_user.user_id)
            )

            try:
                from flask_mail import Message
                from app import mail
                msg = Message(
                    subject    = "SkillLoop – Your Verification Code",
                    sender     = "noreply@skillloop.com",
                    recipients = [current_user.email]
                )
                msg.body = f"""
Hi {current_user.name},

Your SkillLoop verification code is:

        {otp}

This code expires in 10 minutes.
Do not share this code with anyone.

– SkillLoop Team
"""
                mail.send(msg)
                flash(
                    f"📨 Code sent to {current_user.email}! "
                    f"Check your inbox.",
                    "success"
                )
            except Exception:
                # Dev mode – show OTP on screen
                flash(
                    f"Dev Mode – Your OTP is: {otp}",
                    "info"
                )

            return render_template(
                "auth/verify_student.html",
                show_otp_input = True,
                auto_verified  = False,
            )

        # ── Verify OTP ───────────────────────────────────────────
        elif action == "verify_otp":
            entered = request.form.get("otp", "").strip()

            row = execute_query(
                "SELECT otp_code, otp_expiry FROM Users "
                "WHERE user_id=?",
                (current_user.user_id,), fetch="one"
            )

            if not row or not row["otp_code"]:
                flash("No code found. Please request a new one.",
                      "danger")
                return render_template(
                    "auth/verify_student.html",
                    show_otp_input = False,
                    auto_verified  = False,
                )

            # Check expiry
            expiry = row["otp_expiry"]
            if isinstance(expiry, str):
                expiry = datetime.strptime(
                    expiry, "%Y-%m-%d %H:%M:%S.%f"
                )
            if datetime.now() > expiry:
                flash("Code expired. Please request a new one.",
                      "danger")
                return render_template(
                    "auth/verify_student.html",
                    show_otp_input = False,
                    auto_verified  = False,
                )

            # Check code
            if entered != row["otp_code"]:
                flash("Wrong code. Please try again.", "danger")
                return render_template(
                    "auth/verify_student.html",
                    show_otp_input = True,
                    auto_verified  = False,
                )

            # ✅ Correct OTP
            UserModel.verify_user(current_user.user_id, "otp")
            execute_query(
                "UPDATE Users SET otp_code=NULL, "
                "otp_expiry=NULL WHERE user_id=?",
                (current_user.user_id,)
            )
            flash("✅ Verified successfully! Welcome to SkillLoop!",
                  "success")
            return redirect(url_for("auth.profile_setup"))

    return render_template(
        "auth/verify_student.html",
        show_otp_input = False,
        auto_verified  = False,
    )


# ---------------------------------------------------------------
# PROFILE SETUP  /profile-setup
# ---------------------------------------------------------------
@auth_bp.route("/profile-setup", methods=["GET", "POST"])
@login_required
def profile_setup():
    if request.method == "POST":
        role      = request.form.get("role", "buyer")
        bio       = request.form.get("bio", "").strip()
        skills    = request.form.getlist("skills")
        portfolio = request.form.get("portfolio_link", "").strip()

        # Validate role
        valid_roles = UserFactory.get_valid_roles()
        if role not in valid_roles:
            flash("Invalid role selected.", "danger")
            return render_template("auth/profile_setup.html")

        # Update profile
        UserModel.update_profile(
            user_id = current_user.user_id,
            bio     = bio,
        )

        # Apply Factory Pattern – sets role, coins, notification
        profile = UserFactory.create(
            user_id = current_user.user_id,
            role    = role,
        )
        try:
            UserFactory.apply_to_db(current_user.user_id, profile)
        except Exception:
            # DB might not be set up yet — just update role
            UserModel.update_role(current_user.user_id, role)

        # Save skills
        if skills:
            try:
                from app.utils.db import execute_query
                for skill_id in skills:
                    execute_query(
                        """
                        IF NOT EXISTS (
                            SELECT 1 FROM UserSkills
                            WHERE user_id=? AND skill_id=?
                        )
                        INSERT INTO UserSkills (user_id, skill_id)
                        VALUES (?,?)
                        """,
                        (current_user.user_id, skill_id,
                         current_user.user_id, skill_id)
                    )
            except Exception:
                pass

        flash("Profile set up successfully! Welcome to SkillLoop 🎉",
              "success")
        return redirect(url_for("dashboard.index"))

    # GET – load available skills
    try:
        from app.utils.db import execute_query
        all_skills = execute_query(
            "SELECT * FROM Skills ORDER BY category, name",
            fetch="all"
        ) or []
    except Exception:
        all_skills = []

    return render_template("auth/profile_setup.html",
                           all_skills=all_skills)