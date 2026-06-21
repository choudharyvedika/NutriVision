"""
Profile routes — collects the physical stats and goal needed to calculate
BMR / TDEE / daily calorie + macro targets, and lets users update them later.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import WeightLog, ACTIVITY_LABELS, GOAL_LABELS

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    onboarding = request.args.get("onboarding") == "1"

    if request.method == "POST":
        errors = []
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        goal_weight = request.form.get("goal_weight", "")
        activity_level = request.form.get("activity_level", "")
        goal = request.form.get("goal", "")
        water_goal = request.form.get("water_goal_ml", "")

        if len(name) < 2:
            errors.append("Please enter your full name.")

        try:
            age = int(age)
            if not (10 <= age <= 100):
                errors.append("Age must be between 10 and 100.")
        except ValueError:
            errors.append("Please enter a valid age.")

        if gender not in ("male", "female", "other"):
            errors.append("Please select a gender.")

        try:
            height = float(height)
            if not (100 <= height <= 250):
                errors.append("Height must be between 100cm and 250cm.")
        except ValueError:
            errors.append("Please enter a valid height in cm.")

        try:
            weight = float(weight)
            if not (30 <= weight <= 300):
                errors.append("Weight must be between 30kg and 300kg.")
        except ValueError:
            errors.append("Please enter a valid weight in kg.")

        goal_weight_val = None
        if goal_weight:
            try:
                goal_weight_val = float(goal_weight)
            except ValueError:
                errors.append("Please enter a valid goal weight.")

        if activity_level not in ACTIVITY_LABELS:
            errors.append("Please select an activity level.")

        if goal not in GOAL_LABELS:
            errors.append("Please select a goal.")

        try:
            water_goal = int(water_goal) if water_goal else 2000
            if not (500 <= water_goal <= 8000):
                errors.append("Water goal must be between 500ml and 8000ml.")
        except ValueError:
            errors.append("Please enter a valid water goal.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "profile.html",
                activity_labels=ACTIVITY_LABELS,
                goal_labels=GOAL_LABELS,
                onboarding=onboarding,
            )

        is_first_weight_entry = current_user.weight is None

        current_user.name = name
        current_user.age = age
        current_user.gender = gender
        current_user.height = height
        current_user.weight = weight
        current_user.goal_weight = goal_weight_val
        current_user.activity_level = activity_level
        current_user.goal = goal
        current_user.water_goal_ml = water_goal
        db.session.commit()

        # Seed the weight history chart with this value the first time a
        # profile is completed so the Weight Tracker isn't empty on day one.
        if is_first_weight_entry:
            db.session.add(WeightLog(user_id=current_user.id, weight=weight))
            db.session.commit()

        flash("Profile saved! Your calorie and macro targets are updated.", "success")
        return redirect(url_for("dashboard.home"))

    return render_template(
        "profile.html",
        activity_labels=ACTIVITY_LABELS,
        goal_labels=GOAL_LABELS,
        onboarding=onboarding,
    )
