"""
Exercise log routes — page render plus a small JSON API so the page can
add/remove entries without a full reload. Calories burned are computed
server-side from the user's current weight so the figure can't be spoofed.
"""
from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import ExerciseLog, EXERCISE_MET, EXERCISE_LABELS
from utils import estimate_calories_burned

exercise_bp = Blueprint("exercise", __name__)


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


@exercise_bp.route("/exercise")
@login_required
def exercise_page():
    selected_date = _parse_date(request.args.get("date"))
    logs = (
        ExerciseLog.query.filter_by(user_id=current_user.id, date=selected_date)
        .order_by(ExerciseLog.created_at.desc())
        .all()
    )
    total_burned = round(sum(l.calories_burned for l in logs), 0)

    return render_template(
        "exercise_log.html",
        selected_date=selected_date,
        prev_date=selected_date - timedelta(days=1),
        next_date=selected_date + timedelta(days=1),
        is_today=(selected_date == date.today()),
        logs=logs,
        total_burned=total_burned,
        exercise_labels=EXERCISE_LABELS,
    )


@exercise_bp.route("/api/exercise/log", methods=["POST"])
@login_required
def add_exercise_log():
    data = request.get_json(silent=True) or {}

    exercise_type = data.get("exercise_type")
    duration = data.get("duration")
    log_date = _parse_date(data.get("date"))

    if exercise_type not in EXERCISE_MET:
        return jsonify({"error": "Please select a valid exercise type."}), 400

    try:
        duration = int(duration)
        if not (1 <= duration <= 600):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Duration must be between 1 and 600 minutes."}), 400

    calories_burned = estimate_calories_burned(exercise_type, duration, current_user.weight)

    entry = ExerciseLog(
        user_id=current_user.id,
        exercise_type=exercise_type,
        duration=duration,
        calories_burned=calories_burned,
        date=log_date,
    )
    db.session.add(entry)
    db.session.commit()

    logs = ExerciseLog.query.filter_by(user_id=current_user.id, date=log_date).all()
    return jsonify({
        "entry": entry.to_dict(),
        "total_burned": round(sum(l.calories_burned for l in logs), 0),
    }), 201


@exercise_bp.route("/api/exercise/log/<int:log_id>", methods=["DELETE"])
@login_required
def delete_exercise_log(log_id):
    entry = ExerciseLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    log_date = entry.date
    db.session.delete(entry)
    db.session.commit()

    logs = ExerciseLog.query.filter_by(user_id=current_user.id, date=log_date).all()
    return jsonify({"total_burned": round(sum(l.calories_burned for l in logs), 0)})
