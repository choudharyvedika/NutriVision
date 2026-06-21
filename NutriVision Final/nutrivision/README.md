# 🥗 NutriVision

A modern, full-stack calorie and nutrition tracking web app — built with Flask, SQLite, and vanilla JavaScript. Designed to look and feel like a real health-tech SaaS product (think MyFitnessPal × Fitbit × Notion), and structured as a portfolio-ready project.

![Stack](https://img.shields.io/badge/backend-Flask-4CAF50) ![DB](https://img.shields.io/badge/database-SQLite-2E7D32) ![Charts](https://img.shields.io/badge/charts-Chart.js-81C784)

---

## ✨ Features

- **Authentication** — signup / login / logout with hashed passwords (Werkzeug), server-side validation, and session management via Flask-Login
- **Smart Profile** — collects age, gender, height, weight, activity level & goal, then auto-calculates **BMR**, **TDEE**, daily calorie target, and macro targets (Mifflin-St Jeor formula)
- **Dashboard** — signature animated calorie ring, 4 stat cards, macro breakdown bars, today's meals, water + weight widgets, and a 7-day calorie trend chart
- **Food Log** — live search across a 60-food seeded database, quantity + meal-type selection, instant macro preview, AJAX add/remove with zero page reloads
- **Exercise Log** — 5 activity types (walking, running, cycling, gym, yoga) with MET-based calorie burn estimation computed server-side from your weight
- **Water Tracker** — animated ring, one-tap quick-add buttons, custom amounts, editable daily goal, 7-day history bars
- **Weight Tracker** — Chart.js progression line chart with goal-weight target line, full history with edit/delete
- **Reports & Analytics** — Daily / Weekly / Monthly tabs with period navigation, average macros, consistency %, goal adherence %, and dynamic Chart.js visuals
- **Polished UI/UX** — glassmorphism cards, soft shadows, smooth transitions, empty states, flash messages, fully responsive (mobile sidebar drawer)

---

## 🛠 Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | HTML5, CSS3 (custom design system), Vanilla JS |
| Backend    | Python 3, Flask (application factory + blueprints) |
| Database   | SQLite via Flask-SQLAlchemy          |
| Auth       | Flask-Login + Werkzeug password hashing |
| Charts     | Chart.js (CDN)                       |
| Fonts      | Plus Jakarta Sans + Inter (Google Fonts) |

---

## 📁 Project Structure

```
nutrivision/
├── app.py                  # Application factory, blueprint registration, DB bootstrap
├── config.py                # App configuration
├── extensions.py             # Shared db / login_manager instances
├── models.py                 # SQLAlchemy models (Users, Foods, FoodLogs, ExerciseLogs, WaterLogs, WeightLogs)
├── utils.py                  # Calorie-burn estimation, date-range helpers
├── seed_data.py               # Seeds 60 common foods into the database
├── requirements.txt
├── blueprints/
│   ├── auth.py                # signup / login / logout
│   ├── dashboard.py            # home dashboard aggregation
│   ├── profile.py              # profile + BMR/TDEE calculation
│   ├── food.py                 # food search + meal logging API
│   ├── exercise.py             # exercise logging + calorie burn API
│   ├── water.py                # water logging + goal API
│   ├── weight.py               # weight logging + history API
│   └── reports.py              # daily/weekly/monthly analytics API
├── templates/
│   ├── base.html               # sidebar + topbar shell
│   ├── auth/                   # login.html, signup.html
│   ├── partials/icons.html      # shared inline SVG icon set
│   ├── errors/                 # 404.html, 500.html
│   └── *.html                  # dashboard, food_log, exercise_log, water_tracker, weight_tracker, reports, profile
├── static/
│   ├── css/style.css           # full design system (tokens, components, responsive)
│   └── js/                     # main.js + one JS module per page
└── instance/
    └── nutrivision.db          # SQLite database (created automatically)
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

The database is created and seeded with 60 foods automatically on first run. Visit:

```
http://127.0.0.1:5000
```

### 3. Create an account
Sign up, complete the one-step onboarding profile (age, height, weight, activity level, goal), and you'll land on your personalized dashboard with BMR/TDEE-based calorie and macro targets already calculated.

> To reset all data, simply delete `instance/nutrivision.db` and restart the app — it will be recreated and reseeded automatically.

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

- **BMR** — Mifflin-St Jeor equation
- **TDEE** — BMR × activity multiplier (1.2 – 1.9 depending on activity level)
- **Daily Calorie Goal** — TDEE ± 500 kcal based on goal (loss / maintenance / gain)
- **Macro split** — 30% protein / 40% carbs / 30% fat of the daily calorie goal
- **Exercise calories burned** — MET formula: `calories = MET × weight(kg) × duration(hours)`

---

## 📝 Notes

- This is a learning/portfolio MVP — passwords are hashed and sessions are secure, but for a production deployment you'd want HTTPS, a production WSGI server (e.g. Gunicorn), environment-based secrets, and rate limiting on auth routes.
- Built with a modular Flask blueprint architecture so each feature (auth, food, exercise, water, weight, reports) is isolated and easy to extend.
