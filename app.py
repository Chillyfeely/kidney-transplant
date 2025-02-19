from flask import Flask
from extensions import mongo
from waitress import serve
from config import Config
from website.routes import website_bp
from api.database_operations import db_bp
app = Flask(__name__)



app.secret_key = 'devkey'

app.config["MONGO_URI"] = Config.MONGO_URI

mongo.init_app(app)

app.register_blueprint(website_bp)
app.register_blueprint(db_bp)

if __name__ == "__main__":
    # serve(app, host="0.0.0.0", port=5000)
    app.run(host="0.0.0.0", port=5050, debug=True)
