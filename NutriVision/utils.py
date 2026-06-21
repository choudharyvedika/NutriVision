"""
Utility helpers shared across blueprints: exercise calorie estimation
and date-range math used by the reports module.
"""
from datetime import date, timedelta

from models import EXERCISE_MET


def estimate_calories_burned(exercise_type, duration_minutes, weight_kg):
    """
    Estimate calories burned using the standard MET formula:
        calories = MET * weight(kg) * duration(hours)
    Falls back to a moderate MET of 5.0 for unknown exercise types.
    """
    met = EXERCISE_MET.get(exercise_type, 5.0)
    weight_kg = weight_kg or 70  # sensible fallback if profile incomplete
    hours = duration_minutes / 60
    return round(met * weight_kg * hours, 1)


def week_range(anchor_date):
    """Return (monday, sunday) for the week containing anchor_date."""
    start = anchor_date - timedelta(days=anchor_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def month_range(year, month):
    """Return (first_day, last_day) of the given month/year."""
    first_day = date(year, month, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    return first_day, last_day


def daterange(start_date, end_date):
    """Yield each date from start_date to end_date inclusive."""
    days = (end_date - start_date).days
    for n in range(days + 1):
        yield start_date + timedelta(days=n)
