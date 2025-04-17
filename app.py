from flask import Flask
from extensions import mongo
from waitress import serve
from config import Config
from website.routes import website_bp
from api.database_operations import db_bp
from extensions import db, mongo, init_login_manager
app = Flask(__name__)



app.secret_key = 'devkey'

init_login_manager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["MONGO_URI"] = Config.MONGO_URI

db.init_app(app)
mongo.init_app(app)


from models.user import User

with app.app_context():
    db.create_all()

app.register_blueprint(website_bp)
app.register_blueprint(db_bp)

if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=5000)
    app.run(host="0.0.0.0", port=5050, debug=True)
