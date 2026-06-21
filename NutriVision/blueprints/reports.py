"""
Reports & Analytics — daily / weekly / monthly views.

The page itself renders once with today's daily report pre-loaded; switching
tabs or navigating between periods calls the JSON APIs below so the charts
can update without a full page reload.
"""
from datetime import datetime, date

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from models import FoodLog, ExerciseLog, WeightLog
from utils import week_range, month_range, daterange

reports_bp = Blueprint("reports", __name__)


def _parse_date(value, default=None):
    if not value:
        return default or date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default or date.today()


def _day_summary(user_id, day):
    food_logs = FoodLog.query.filter_by(user_id=user_id, date=day).all()
    exercise_logs = ExerciseLog.query.filter_by(user_id=user_id, date=day).all()
    return {
        "date": day.isoformat(),
        "calories_consumed": round(sum(l.calories for l in food_logs), 0),
        "calories_burned": round(sum(l.calories_burned for l in exercise_logs), 0),
        "protein": round(sum(l.protein for l in food_logs), 1),
        "carbs": round(sum(l.carbs for l in food_logs), 1),
        "fat": round(sum(l.fat for l in food_logs), 1),
        "logged": len(food_logs) > 0,
    }


@reports_bp.route("/reports")
@login_required
def reports_page():
    today = date.today()
    daily = _day_summary(current_user.id, today)
    calorie_goal = current_user.calculate_daily_calorie_goal() or 2000
    macro_targets = current_user.calculate_macro_targets()

    return render_template(
        "reports.html",
        today=today,
        daily=daily,
        calorie_goal=calorie_goal,
        macro_targets=macro_targets,
    )


@reports_bp.route("/api/reports/daily")
@login_required
def api_daily_report():
    day = _parse_date(request.args.get("date"))
    summary = _day_summary(current_user.id, day)
    summary["calorie_goal"] = current_user.calculate_daily_calorie_goal() or 2000
    summary["macro_targets"] = current_user.calculate_macro_targets()
    return jsonify(summary)


@reports_bp.route("/api/reports/weekly")
@login_required
def api_weekly_report():
    anchor = _parse_date(request.args.get("start"))
    start, end = week_range(anchor)

    days = [_day_summary(current_user.id, d) for d in daterange(start, end)]
    logged_days = [d for d in days if d["logged"]]
    n = len(logged_days) or 1

    avg_calories = round(sum(d["calories_consumed"] for d in logged_days) / n, 0)
    avg_protein = round(sum(d["protein"] for d in logged_days) / n, 1)
    avg_carbs = round(sum(d["carbs"] for d in logged_days) / n, 1)
    avg_fat = round(sum(d["fat"] for d in logged_days) / n, 1)

    weight_logs = (
        WeightLog.query.filter(
            WeightLog.user_id == current_user.id,
            WeightLog.date >= start,
            WeightLog.date <= end,
        )
        .order_by(WeightLog.date.asc())
        .all()
    )
    weight_change = None
    if len(weight_logs) >= 2:
        weight_change = round(weight_logs[-1].weight - weight_logs[0].weight, 1)

    return jsonify({
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
        "avg_calories": avg_calories,
        "avg_protein": avg_protein,
        "avg_carbs": avg_carbs,
        "avg_fat": avg_fat,
        "weight_change": weight_change,
        "days_logged": len(logged_days),
        "calorie_goal": current_user.calculate_daily_calorie_goal() or 2000,
    })


@reports_bp.route("/api/reports/monthly")
@login_required
def api_monthly_report():
    today = date.today()
    year = int(request.args.get("year", today.year))
    month = int(request.args.get("month", today.month))
    start, end = month_range(year, month)
    end = min(end, today) if (year, month) == (today.year, today.month) else end

    days = [_day_summary(current_user.id, d) for d in daterange(start, end)]
    logged_days = [d for d in days if d["logged"]]
    total_days = len(days) or 1

    calorie_goal = current_user.calculate_daily_calorie_goal() or 2000
    # Goal adherence: days where intake landed within 80%-100% of goal (i.e. on or under target).
    on_target_days = [
        d for d in logged_days if calorie_goal * 0.8 <= d["calories_consumed"] <= calorie_goal
    ]
    adherence_pct = round((len(on_target_days) / len(logged_days)) * 100, 0) if logged_days else 0
    consistency_pct = round((len(logged_days) / total_days) * 100, 0)

    weight_logs = (
        WeightLog.query.filter(
            WeightLog.user_id == current_user.id,
            WeightLog.date >= start,
            WeightLog.date <= end,
        )
        .order_by(WeightLog.date.asc())
        .all()
    )
    weight_change = None
    if len(weight_logs) >= 2:
        weight_change = round(weight_logs[-1].weight - weight_logs[0].weight, 1)

    avg_calories = round(sum(d["calories_consumed"] for d in logged_days) / len(logged_days), 0) if logged_days else 0
    avg_protein = round(sum(d["protein"] for d in logged_days) / len(logged_days), 1) if logged_days else 0
    avg_carbs = round(sum(d["carbs"] for d in logged_days) / len(logged_days), 1) if logged_days else 0
    avg_fat = round(sum(d["fat"] for d in logged_days) / len(logged_days), 1) if logged_days else 0

    return jsonify({
        "year": year,
        "month": month,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
        "avg_calories": avg_calories,
        "avg_protein": avg_protein,
        "avg_carbs": avg_carbs,
        "avg_fat": avg_fat,
        "consistency_pct": consistency_pct,
        "adherence_pct": adherence_pct,
        "weight_change": weight_change,
        "days_logged": len(logged_days),
        "total_days": total_days,
        "calorie_goal": calorie_goal,
    })
