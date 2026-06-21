"""
Water tracker routes — quick-add buttons (+250ml etc.), a custom amount
field, and a way to change the daily goal, all driven through small JSON
endpoints so the progress ring updates instantly.
"""
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import WaterLog

water_bp = Blueprint("water", __name__)


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@water_bp.route("/water")
@login_required
def water_page():
    selected_date = _parse_date(request.args.get("date"))
    logs = (
        WaterLog.query.filter_by(user_id=current_user.id, date=selected_date)
        .order_by(WaterLog.created_at.desc())
        .all()
    )
    total = sum(l.amount for l in logs)

    # Last 7 days for the mini history bars.
    history = []
    today = date.today()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = sum(
            l.amount for l in WaterLog.query.filter_by(user_id=current_user.id, date=day).all()
        )
        history.append({"label": day.strftime("%a"), "amount": day_total})

    return render_template(
        "water_tracker.html",
        selected_date=selected_date,
        prev_date=selected_date - timedelta(days=1),
        next_date=selected_date + timedelta(days=1),
        is_today=(selected_date == date.today()),
        logs=logs,
        total=total,
        goal=current_user.water_goal_ml,
        history=history,
    )


@water_bp.route("/api/water/log", methods=["POST"])
@login_required
def add_water_log():
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")
    log_date = _parse_date(data.get("date"))

    try:
        amount = int(amount)
        if not (1 <= amount <= 5000):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Amount must be between 1ml and 5000ml."}), 400

    entry = WaterLog(user_id=current_user.id, amount=amount, date=log_date)
    db.session.add(entry)
    db.session.commit()

    logs = WaterLog.query.filter_by(user_id=current_user.id, date=log_date).all()
    return jsonify({
        "entry": entry.to_dict(),
        "total": sum(l.amount for l in logs),
        "goal": current_user.water_goal_ml,
    }), 201


@water_bp.route("/api/water/log/<int:log_id>", methods=["DELETE"])
@login_required
def delete_water_log(log_id):
    entry = WaterLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    log_date = entry.date
    db.session.delete(entry)
    db.session.commit()

    logs = WaterLog.query.filter_by(user_id=current_user.id, date=log_date).all()
    return jsonify({"total": sum(l.amount for l in logs)})


@water_bp.route("/api/water/goal", methods=["POST"])
@login_required
def update_water_goal():
    data = request.get_json(silent=True) or {}
    try:
        goal = int(data.get("goal"))
        if not (500 <= goal <= 8000):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Goal must be between 500ml and 8000ml."}), 400

    current_user.water_goal_ml = goal
    db.session.commit()
    return jsonify({"goal": goal})
