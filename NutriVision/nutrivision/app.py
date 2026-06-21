"""
NutriVision — Flask application entry point.

Run with:   python app.py
The app factory pattern keeps the project modular: extensions, models and
blueprints are wired together here instead of all living in one file.
"""
from datetime import date

from flask import Flask, render_template, redirect, url_for
from flask_login import current_user

from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy is aware of them before create_all().
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- Register blueprints ---
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.profile import profile_bp
    from blueprints.food import food_bp
    from blueprints.exercise import exercise_bp
    from blueprints.water import water_bp
    from blueprints.weight import weight_bp
    from blueprints.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(weight_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.home"))
        return redirect(url_for("auth.login"))

    # Friendly error pages so the app never shows a raw stack trace to users.
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Make "today" available in every template for nav highlighting / date pickers.
    @app.context_processor
    def inject_today():
        return {"today": date.today()}

    # Create tables + seed the food database automatically on first boot.
    with app.app_context():
        db.create_all()
        from seed_data import seed_foods
        seed_foods()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
