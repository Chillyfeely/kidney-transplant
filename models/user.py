from extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    user_id = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return self.user_id