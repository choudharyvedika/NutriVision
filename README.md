# 🥗 NutriVision

A full-stack calorie and nutrition tracking web app built with Flask, SQLite, and vanilla JavaScript — designed to look and feel like a real health-tech product (think MyFitnessPal × Fitbit × Notion).

![Python](https://img.shields.io/badge/python-3.x-blue) ![Flask](https://img.shields.io/badge/backend-Flask-4CAF50) ![DB](https://img.shields.io/badge/database-SQLite-2E7D32) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

- **Authentication** — signup / login / logout with hashed passwords (Werkzeug) and session management via Flask-Login
- **Smart Profile** — collects age, gender, height, weight, activity level & goal, then auto-calculates **BMR**, **TDEE**, daily calorie target, and macro targets (Mifflin-St Jeor equation)
- **Dashboard** — calorie ring, stat cards, macro breakdown, today's meals, water + weight widgets
- **Food Log** — search across a seeded food database, log by quantity and meal type (breakfast / lunch / dinner / snacks)
- **Exercise Log** — walking, running, cycling, gym workout, and yoga, with MET-based calorie burn estimated from the user's weight
- **Water Tracker** — daily intake logging against a configurable goal
- **Weight Tracker** — weight history logging toward a goal weight
- **Reports & Analytics** — daily / weekly / monthly views built from logged data

---

## 🛠 Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python 3, Flask (application factory + blueprints) |
| Database   | SQLite via Flask-SQLAlchemy |
| Auth       | Flask-Login + Werkzeug password hashing |
| Frontend   | HTML, CSS, vanilla JavaScript (templates/static, rendered server-side) |

---

## 📁 Project Structure

```
nutrivision/
├── app.py              # Application factory, blueprint registration, DB bootstrap
├── config.py           # App configuration (env-driven, sane dev defaults)
├── extensions.py        # Shared db / login_manager instances
├── models.py             # SQLAlchemy models: User, Food, FoodLog, ExerciseLog, WaterLog, WeightLog
├── utils.py               # Calorie-burn estimation, date-range helpers for reports
├── seed_data.py             # Seeds the foods table with a starter food database
├── requirements.txt
├── blueprints/               # auth, dashboard, profile, food, exercise, water, weight, reports
├── templates/                 # Jinja templates (base shell, auth, errors, per-feature pages)
├── static/                     # CSS and JS assets
└── instance/
    └── nutrivision.db          # SQLite database (created automatically on first run)
```

> Note: `blueprints/`, `templates/`, and `static/` are referenced by `app.py` and expected by the project layout but weren't included in this file set — make sure they're present in your working copy.

---

## 🚀 Getting Started

### 1. Clone and install dependencies
```bash
git clone <your-repo-url>
cd nutrivision
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

On first run, `app.py` calls `db.create_all()` and `seed_foods()` automatically, so the database is created and pre-populated with common foods with no extra setup. Then visit:

```
http://127.0.0.1:5000
```

### 3. Create an account
Sign up, complete your profile (age, height, weight, activity level, goal), and you'll land on a dashboard with BMR/TDEE-based calorie and macro targets already calculated.

> To reset all data, delete `instance/nutrivision.db` and restart the app — it will be recreated and reseeded automatically.

---

## 🗄️ Database Schema

| Table           | Key Fields |
|-----------------|------------|
| `users`         | name, email, password_hash, age, gender, height, weight, goal_weight, activity_level, goal, water_goal_ml |
| `foods`         | food_name, category, serving_size, calories, protein, carbs, fat |
| `food_logs`     | user_id, food_id, quantity, meal_type, date |
| `exercise_logs` | user_id, exercise_type, duration, calories_burned, date |
| `water_logs`    | user_id, amount, date |
| `weight_logs`   | user_id, weight, date |

## 🧮 Calculation Methodology

- **BMR** — Mifflin-St Jeor equation (differs slightly for male / female / other)
- **TDEE** — BMR × activity multiplier (1.2 for sedentary up to 1.9 for extremely active)
- **Daily Calorie Goal** — TDEE ± 500 kcal depending on goal (loss / maintenance / gain), floored at 1200 kcal
- **Macro split** — 30% protein / 40% carbs / 30% fat of the daily calorie goal
- **Exercise calories burned** — MET formula: `calories = MET × weight(kg) × duration(hours)`, defaulting to MET 5.0 for unrecognized exercise types

---

## ⚙️ Configuration

Environment variables (see `config.py`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | dev placeholder | Signs session cookies — **set this in production** |
| `DATABASE_URL` | local SQLite file in `instance/` | Override to point at another database |

---

## 📝 Notes

- This is a learning/portfolio project — passwords are hashed and sessions are secure, but a production deployment would also want HTTPS, a production WSGI server (e.g. Gunicorn), environment-based secrets, and rate limiting on auth routes.
- Built with a modular Flask blueprint architecture so each feature (auth, food, exercise, water, weight, reports) is isolated and easy to extend.

## 📄 License

MIT — feel free to fork and build on this.
