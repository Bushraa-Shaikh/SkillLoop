import os
import logging
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from config.config import config_map

login_manager = LoginManager()
mail = Mail()

try:
    from flask_socketio import SocketIO
    socketio = SocketIO()
    _socketio_available = True
except ImportError:
    socketio = None
    _socketio_available = False


def create_app(env="default"):
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    cfg = config_map.get(env, config_map["default"])
    app.config.from_object(cfg)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in."
    login_manager.login_message_category = "warning"
    mail.init_app(app)

    if _socketio_available and socketio:
        socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    from app.models.user import UserModel

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.get_by_id(int(user_id))

    from app.controllers.main      import main_bp
    from app.controllers.auth      import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.gigs      import gigs_bp
    from app.controllers.orders    import orders_bp
    from app.controllers.chat      import chat_bp
    from app.controllers.wallet    import wallet_bp
    from app.controllers.projects  import projects_bp
    from app.controllers.admin     import admin_bp
    from app.controllers.profile   import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,      url_prefix="/")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(gigs_bp,      url_prefix="/")
    app.register_blueprint(orders_bp,    url_prefix="/")
    app.register_blueprint(chat_bp,      url_prefix="/")
    app.register_blueprint(wallet_bp,    url_prefix="/")
    app.register_blueprint(projects_bp,  url_prefix="/")
    app.register_blueprint(admin_bp,     url_prefix="/admin")
    app.register_blueprint(profile_bp,   url_prefix="/")

    from app.utils.helpers import time_ago, format_date

    @app.context_processor
    def utility_processor():
        return {"time_ago": time_ago, "format_date": format_date}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    if _socketio_available and socketio:
        from app.controllers.chat import register_socketio_events
        register_socketio_events()

    return app
