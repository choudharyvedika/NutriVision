"""
Food log routes.

`/food` renders the meal-logging page for a given date (defaults to today).
The `/api/food/*` endpoints power the live search box and AJAX add/delete
interactions on that page so users never need a full-page reload.
"""
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Food, FoodLog, MEAL_TYPES

food_bp = Blueprint("food", __name__)


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def _day_totals(user_id, day):
    logs = FoodLog.query.filter_by(user_id=user_id, date=day).all()
    return {
        "calories": round(sum(l.calories for l in logs), 1),
        "protein": round(sum(l.protein for l in logs), 1),
        "carbs": round(sum(l.carbs for l in logs), 1),
        "fat": round(sum(l.fat for l in logs), 1),
    }


@food_bp.route("/food")
@login_required
def food_log_page():
    selected_date = _parse_date(request.args.get("date"))
    logs = FoodLog.query.filter_by(user_id=current_user.id, date=selected_date).all()

    meals = {meal: [] for meal in MEAL_TYPES}
    for log in logs:
        meals[log.meal_type].append(log)

    totals = _day_totals(current_user.id, selected_date)
    macro_targets = current_user.calculate_macro_targets()
    calorie_goal = current_user.calculate_daily_calorie_goal() or 2000

    return render_template(
        "food_log.html",
        selected_date=selected_date,
        prev_date=selected_date - timedelta(days=1),
        next_date=selected_date + timedelta(days=1),
        is_today=(selected_date == date.today()),
        meals=meals,
        totals=totals,
        macro_targets=macro_targets,
        calorie_goal=calorie_goal,
        meal_types=MEAL_TYPES,
    )


@food_bp.route("/api/food/search")
@login_required
def search_foods():
    query = request.args.get("q", "").strip()
    if len(query) < 1:
        return jsonify({"foods": []})

    matches = (
        Food.query.filter(Food.food_name.ilike(f"%{query}%"))
        .order_by(Food.food_name)
        .limit(20)
        .all()
    )
    return jsonify({"foods": [f.to_dict() for f in matches]})


@food_bp.route("/api/food/log", methods=["POST"])
@login_required
def add_food_log():
    data = request.get_json(silent=True) or {}

    food_id = data.get("food_id")
    meal_type = data.get("meal_type")
    quantity = data.get("quantity", 1)
    log_date = _parse_date(data.get("date"))

    if meal_type not in MEAL_TYPES:
        return jsonify({"error": "Invalid meal type."}), 400

    food = db.session.get(Food, food_id) if food_id is not None else None
    if food is None:
        return jsonify({"error": "Food not found."}), 404

    try:
        quantity = float(quantity)
        if quantity <= 0 or quantity > 50:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity must be a positive number."}), 400

    entry = FoodLog(
        user_id=current_user.id,
        food_id=food.id,
        quantity=quantity,
        meal_type=meal_type,
        date=log_date,
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"entry": entry.to_dict(), "totals": _day_totals(current_user.id, log_date)}), 201


@food_bp.route("/api/food/log/<int:log_id>", methods=["DELETE"])
@login_required
def delete_food_log(log_id):
    entry = FoodLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    log_date = entry.date
    db.session.delete(entry)
    db.session.commit()

    return jsonify({"totals": _day_totals(current_user.id, log_date)})
