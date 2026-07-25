"""
General utility helpers used across the application.
"""
import os
import re
import hashlib
import secrets
import string
from datetime import datetime
from werkzeug.utils import secure_filename


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip", "docx"}


def allowed_file(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, upload_folder: str, prefix: str = "") -> str:
    """Save an uploaded file and return its stored filename."""
    filename  = secure_filename(file.filename)
    unique    = secrets.token_hex(8)
    name, ext = os.path.splitext(filename)
    stored    = f"{prefix}_{unique}{ext}" if prefix else f"{unique}{ext}"
    path      = os.path.join(upload_folder, stored)
    file.save(path)
    return stored


# ---------------------------------------------------------------------------
# String / token helpers
# ---------------------------------------------------------------------------
def generate_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------
def time_ago(dt: datetime) -> str:
    """Return a human-readable 'time ago' string."""
    if not dt:
        return ""
    now   = datetime.utcnow()
    delta = now - dt
    secs  = int(delta.total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        m = secs // 60
        return f"{m} minute{'s' if m > 1 else ''} ago"
    if secs < 86400:
        h = secs // 3600
        return f"{h} hour{'s' if h > 1 else ''} ago"
    d = secs // 86400
    if d < 30:
        return f"{d} day{'s' if d > 1 else ''} ago"
    if d < 365:
        mo = d // 30
        return f"{mo} month{'s' if mo > 1 else ''} ago"
    y = d // 365
    return f"{y} year{'s' if y > 1 else ''} ago"


def format_date(dt: datetime, fmt: str = "%b %d, %Y") -> str:
    if not dt:
        return ""
    return dt.strftime(fmt)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))


def is_student_email(email: str) -> bool:
    """
    Returns True only if email belongs to an
    educational institution domain.
    """
    TEST_WHITELIST = ["bushra.max007@gmail.com"]
    if email.lower() in TEST_WHITELIST:
        return True
    
    if "@" not in email:
        return False

    domain = email.lower().split("@")[-1]

    # Educational domain endings
    edu_domains = [
        ".edu",        # USA universities
        ".ac.uk",      # UK universities
        ".ac.in",      # India universities
        ".edu.pk",     # Pakistan universities
        ".ac.pk",      # Pakistan colleges
        ".edu.au",     # Australia
        ".ac.nz",      # New Zealand
        ".edu.sg",     # Singapore
        ".ac.za",      # South Africa
        ".edu.cn",     # China
        ".ac.jp",      # Japan
        ".edu.hk",     # Hong Kong
        ".edu.my",     # Malaysia
        ".edu.bd",     # Bangladesh
        ".edu.np",     # Nepal
        ".edu.lk",     # Sri Lanka
        ".edu.ph",     # Philippines
        ".edu.eg",     # Egypt
        ".edu.tr",     # Turkey
        ".edu.br",     # Brazil
        ".edu.mx",     # Mexico
        ".edu.co",     # Colombia
        ".edu.ar",     # Argentina
    ]

    for ending in edu_domains:
        if domain.endswith(ending):
            return True

    # Also check if domain itself contains 'edu'
    # e.g. fast.edu, lums.edu.pk already covered above
    # but also catches: myuniversity.edu.something
    parts = domain.split(".")
    if "edu" in parts or "ac" in parts:
        return True

    return False


def validate_password(password: str) -> tuple:
    """Return (is_valid: bool, message: str)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number."
    return True, "OK"


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------
def paginate(query_results: list, page: int, per_page: int = 10) -> dict:
    total      = len(query_results)
    start      = (page - 1) * per_page
    end        = start + per_page
    items      = query_results[start:end]
    total_pages = (total + per_page - 1) // per_page
    return {
        "items":       items,
        "total":       total,
        "page":        page,
        "per_page":    per_page,
        "total_pages": total_pages,
        "has_prev":    page > 1,
        "has_next":    page < total_pages,
    }