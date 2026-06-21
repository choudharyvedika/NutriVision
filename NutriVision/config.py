"""
Application configuration.

Reads sensitive values from environment variables where possible and
falls back to sane development defaults so the project runs out of the box.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Used to sign session cookies - override via env var in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "nutrivision-dev-secret-change-me")

    # SQLite database lives inside /instance so it is gitignored by default
    # and kept separate from application code.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'nutrivision.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default daily water goal (in millilitres) assigned to new users.
    DEFAULT_WATER_GOAL_ML = 2000

    # Default macro split applied when computing macro gram targets.
    MACRO_SPLIT = {"protein": 0.30, "carbs": 0.40, "fat": 0.30}
