"""
Weight tracker routes — log new entries and view progression against the
user's goal weight. The chart is rendered client-side with Chart.js using
data from /api/weight/log.
"""
from datetime import date, datetime

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import WeightLog

weight_bp = Blueprint("weight", __name__)


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@weight_bp.route("/weight")
@login_required
def weight_page():
    logs = (
        WeightLog.query.filter_by(user_id=current_user.id)
        .order_by(WeightLog.date.asc())
        .all()
    )

    starting_weight = logs[0].weight if logs else current_user.weight
    latest_weight = logs[-1].weight if logs else current_user.weight
    change = round(latest_weight - starting_weight, 1) if logs else 0

    return render_template(
        "weight_tracker.html",
        logs=list(reversed(logs)),  # newest first for the table
        chart_data=[l.to_dict() for l in logs],  # chronological for the chart
        starting_weight=starting_weight,
        latest_weight=latest_weight,
        goal_weight=current_user.goal_weight,
        change=change,
    )


@weight_bp.route("/api/weight/log", methods=["GET"])
@login_required
def get_weight_logs():
    logs = (
        WeightLog.query.filter_by(user_id=current_user.id)
        .order_by(WeightLog.date.asc())
        .all()
    )
    return jsonify({"logs": [l.to_dict() for l in logs], "goal_weight": current_user.goal_weight})


@weight_bp.route("/api/weight/log", methods=["POST"])
@login_required
def add_weight_log():
    data = request.get_json(silent=True) or {}
    weight = data.get("weight")
    log_date = _parse_date(data.get("date"))

    try:
        weight = float(weight)
        if not (30 <= weight <= 300):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Weight must be between 30kg and 300kg."}), 400

    # Replace existing entry for that date if one exists (one entry/day).
    existing = WeightLog.query.filter_by(user_id=current_user.id, date=log_date).first()
    if existing:
        existing.weight = weight
        entry = existing
    else:
        entry = WeightLog(user_id=current_user.id, weight=weight, date=log_date)
        db.session.add(entry)

    # Keep the profile's "current weight" (used in BMR/TDEE) in sync with
    # the most recent entry.
    latest = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.date.desc()).first()
    if latest is None or log_date >= latest.date:
        current_user.weight = weight

    db.session.commit()

    logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.date.asc()).all()
    return jsonify({"entry": entry.to_dict(), "logs": [l.to_dict() for l in logs]}), 201


@weight_bp.route("/api/weight/log/<int:log_id>", methods=["DELETE"])
@login_required
def delete_weight_log(log_id):
    entry = WeightLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    db.session.delete(entry)
    db.session.commit()

    logs = WeightLog.query.filter_by(user_id=current_user.id).order_by(WeightLog.date.asc()).all()
    return jsonify({"logs": [l.to_dict() for l in logs]})
