from flask import Flask
from .config import Config
from .database.models import db
from .routes.main import main_bp
from .routes.auth import auth_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
