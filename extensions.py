from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_login import LoginManager
from datetime import timedelta
from flask import redirect, url_for

db = SQLAlchemy()
mongo = PyMongo()
login_manager = LoginManager()


def init_login_manager(app):
    login_manager.init_app(app)
    login_manager.login_view = "website.login"
    login_manager.remember_cookie_duration = timedelta(days=7)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User

        return User.query.get(str(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("website.login"))

    return login_manager