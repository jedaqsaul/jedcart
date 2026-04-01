import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///jedcart.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-jwt-secret")

    # ── JWT settings ──
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)    # token valid for 7 days
    JWT_TOKEN_LOCATION = ["headers"]                 # look for token in Authorization header
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"