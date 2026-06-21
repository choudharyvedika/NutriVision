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

    # Locally this falls back to a SQLite file. In production (e.g. Vercel),
    # set DATABASE_URL to a Postgres connection string — Vercel's filesystem
    # is read-only at runtime, so SQLite can't be written to there.
    _database_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'nutrivision.db')}"
    )
    # Some providers (Neon, Heroku-style URLs) hand back "postgres://", but
    # SQLAlchemy 1.4+ requires the "postgresql://" scheme — normalize it.
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default daily water goal (in millilitres) assigned to new users.
    DEFAULT_WATER_GOAL_ML = 2000

    # Default macro split applied when computing macro gram targets.
    MACRO_SPLIT = {"protein": 0.30, "carbs": 0.40, "fat": 0.30}
