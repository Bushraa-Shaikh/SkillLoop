import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = False
    TESTING = False

    # SQL Server connection string
    DB_SERVER   = os.environ.get("DB_SERVER", "localhost")
    DB_NAME     = os.environ.get("DB_NAME", "skillloop_db")
    DB_USERNAME = os.environ.get("DB_USERNAME", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

    @staticmethod
    def get_connection_string():
        server   = os.environ.get("DB_SERVER",   "localhost")
        db       = os.environ.get("DB_NAME",     "skillloop_db")
        username = os.environ.get("DB_USERNAME", "")
        password = os.environ.get("DB_PASSWORD", "")

        if not username:
            # Windows Authentication
            return (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={db};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        # SQL Server Authentication
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={db};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )

    # Google OAuth
    GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI  = os.environ.get("GOOGLE_REDIRECT_URI",
                                          "http://localhost:5000/auth/google/callback")
    GOOGLE_AUTH_URL      = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL     = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_SCOPE         = "openid email profile"

    # Mail
    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")

    # App Settings
    APP_URL         = os.environ.get("APP_URL", "http://localhost:5000")
    INITIAL_COINS   = int(os.environ.get("INITIAL_COINS", 100))
    MAX_GIG_IMAGES  = 5
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "zip"}

    # Login manager
    LOGIN_VIEW      = "auth.login"
    LOGIN_MESSAGE   = "Please log in to access this page."


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG   = True


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}