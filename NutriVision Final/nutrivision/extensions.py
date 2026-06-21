"""
Shared Flask extension instances.

Kept in their own module so blueprints can import `db` / `login_manager`
without triggering circular imports with app.py.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access NutriVision."
login_manager.login_message_category = "info"
