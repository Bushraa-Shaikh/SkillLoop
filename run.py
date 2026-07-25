"""
Entry point for the SkillLoop application.
Run with:  python run.py
"""
import os
from app import create_app, socketio

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config["DEBUG"],
    )