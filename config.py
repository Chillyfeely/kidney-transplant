import os

class Config:
    MONGO_URI = "mongodb://localhost:27017/kidney-transplant"
    DB_PATH = os.path.join("database", "app.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.abspath(DB_PATH)}"