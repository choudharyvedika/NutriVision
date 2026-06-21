"""
Dashboard — the main landing page after login. Aggregates "today's" data
from every tracker into the cards/widgets/rings shown on the home screen.
"""
from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import FoodLog, ExerciseLog, WaterLog, WeightLog, MEAL_TYPES

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def home():
    if not current_user.profile_complete:
        return redirect(url_for("profile.edit_profile", onboarding=1))

    today = date.today()

    food_logs = FoodLog.query.filter_by(user_id=current_user.id, date=today).all()
    exercise_logs = ExerciseLog.query.filter_by(user_id=current_user.id, date=today).all()
    water_logs = WaterLog.query.filter_by(user_id=current_user.id, date=today).all()

    calories_consumed = sum(log.calories for log in food_logs)
    protein_consumed = sum(log.protein for log in food_logs)
    carbs_consumed = sum(log.carbs for log in food_logs)
    fat_consumed = sum(log.fat for log in food_logs)
    calories_burned = sum(log.calories_burned for log in exercise_logs)
    water_consumed = sum(log.amount for log in water_logs)

    calorie_goal = current_user.calculate_daily_calorie_goal() or 2000
    macro_targets = current_user.calculate_macro_targets()
    remaining_calories = calorie_goal - calories_consumed + calories_burned

    # Meal breakdown for the "today's meals" widget.
    meals = {meal: [] for meal in MEAL_TYPES}
    for log in food_logs:
        meals[log.meal_type].append(log)
    meal_totals = {
        meal: round(sum(l.calories for l in logs), 0) for meal, logs in meals.items()
    }

    # Weight progress (latest entry vs goal).
    latest_weight_log = (
        WeightLog.query.filter_by(user_id=current_user.id)
        .order_by(WeightLog.date.desc(), WeightLog.id.desc())
        .first()
    )
    latest_weight = latest_weight_log.weight if latest_weight_log else current_user.weight

    # Last 7 days of calories for the mini trend chart.
    trend_labels, trend_calories = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = sum(
            log.calories
            for log in FoodLog.query.filter_by(user_id=current_user.id, date=day).all()
        )
        trend_labels.append(day.strftime("%a"))
        trend_calories.append(round(day_total, 0))

    return render_template(
        "dashboard.html",
        today=today,
        calorie_goal=calorie_goal,
        calories_consumed=round(calories_consumed, 0),
        calories_burned=round(calories_burned, 0),
        remaining_calories=round(remaining_calories, 0),
        macro_targets=macro_targets,
        protein_consumed=round(protein_consumed, 1),
        carbs_consumed=round(carbs_consumed, 1),
        fat_consumed=round(fat_consumed, 1),
        water_consumed=water_consumed,
        water_goal=current_user.water_goal_ml,
        meals=meals,
        meal_totals=meal_totals,
        latest_weight=latest_weight,
        goal_weight=current_user.goal_weight,
        bmr=current_user.calculate_bmr(),
        tdee=current_user.calculate_tdee(),
        trend_labels=trend_labels,
        trend_calories=trend_calories,
    )
