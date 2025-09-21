# config.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")

    # DB
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    # Flask
    JSON_SORT_KEYS = False