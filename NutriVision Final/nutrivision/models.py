"""
Database models for NutriVision.

Tables:
    users         - account + profile + goal data
    foods         - reference food database (seeded)
    food_logs     - a user's logged food entries per meal/day
    exercise_logs - a user's logged workouts
    water_logs    - a user's logged water intake
    weight_logs   - a user's weight history
"""
from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.9,
}

ACTIVITY_LABELS = {
    "sedentary": "Sedentary",
    "lightly_active": "Lightly Active",
    "moderately_active": "Moderately Active",
    "very_active": "Very Active",
    "extremely_active": "Extremely Active",
}

GOAL_LABELS = {
    "weight_loss": "Weight Loss",
    "maintenance": "Maintenance",
    "weight_gain": "Weight Gain",
}

GOAL_CALORIE_ADJUSTMENT = {
    "weight_loss": -500,
    "maintenance": 0,
    "weight_gain": 500,
}

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snacks"]

# MET (Metabolic Equivalent of Task) values used to estimate calories burned.
EXERCISE_MET = {
    "walking": 3.8,
    "running": 9.8,
    "cycling": 7.5,
    "gym_workout": 6.0,
    "yoga": 2.5,
}

EXERCISE_LABELS = {
    "walking": "Walking",
    "running": "Running",
    "cycling": "Cycling",
    "gym_workout": "Gym Workout",
    "yoga": "Yoga",
}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))  # 'male' | 'female' | 'other'
    height = db.Column(db.Float)  # centimetres
    weight = db.Column(db.Float)  # kilograms (latest known weight)
    goal_weight = db.Column(db.Float)  # kilograms (target weight)
    activity_level = db.Column(db.String(30), default="sedentary")
    goal = db.Column(db.String(20), default="maintenance")  # weight_loss | maintenance | weight_gain
    water_goal_ml = db.Column(db.Integer, default=2000)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_logs = db.relationship("FoodLog", backref="user", lazy=True, cascade="all, delete-orphan")
    exercise_logs = db.relationship("ExerciseLog", backref="user", lazy=True, cascade="all, delete-orphan")
    water_logs = db.relationship("WaterLog", backref="user", lazy=True, cascade="all, delete-orphan")
    weight_logs = db.relationship("WeightLog", backref="user", lazy=True, cascade="all, delete-orphan")

    # ---------- Auth helpers ----------
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    # ---------- Profile completeness ----------
    @property
    def profile_complete(self):
        return all([self.age, self.gender, self.height, self.weight, self.activity_level, self.goal])

    # ---------- Nutrition calculations ----------
    def calculate_bmr(self):
        """Mifflin-St Jeor Equation. Returns None if profile data is incomplete."""
        if not all([self.weight, self.height, self.age, self.gender]):
            return None
        base = (10 * self.weight) + (6.25 * self.height) - (5 * self.age)
        if self.gender == "male":
            return round(base + 5, 1)
        elif self.gender == "female":
            return round(base - 161, 1)
        else:
            # Average of male/female offsets for non-binary / unspecified.
            return round(base - 78, 1)

    def calculate_tdee(self):
        bmr = self.calculate_bmr()
        if bmr is None:
            return None
        multiplier = ACTIVITY_MULTIPLIERS.get(self.activity_level, 1.2)
        return round(bmr * multiplier, 1)

    def calculate_daily_calorie_goal(self):
        tdee = self.calculate_tdee()
        if tdee is None:
            return None
        adjustment = GOAL_CALORIE_ADJUSTMENT.get(self.goal, 0)
        goal_calories = tdee + adjustment
        # Keep a sensible floor so suggestions never go dangerously low.
        return round(max(goal_calories, 1200), 0)

    def calculate_macro_targets(self):
        """Returns target grams of protein/carbs/fat based on a 30/40/30 split."""
        calorie_goal = self.calculate_daily_calorie_goal()
        if calorie_goal is None:
            return {"protein": 0, "carbs": 0, "fat": 0}
        return {
            "protein": round((calorie_goal * 0.30) / 4, 0),
            "carbs": round((calorie_goal * 0.40) / 4, 0),
            "fat": round((calorie_goal * 0.30) / 9, 0),
        }

    def __repr__(self):
        return f"<User {self.email}>"


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(50), default="General")
    serving_size = db.Column(db.String(50), default="100 g")  # human readable serving description
    calories = db.Column(db.Float, nullable=False)  # per 1 serving
    protein = db.Column(db.Float, nullable=False)  # grams per 1 serving
    carbs = db.Column(db.Float, nullable=False)  # grams per 1 serving
    fat = db.Column(db.Float, nullable=False)  # grams per 1 serving

    def to_dict(self):
        return {
            "id": self.id,
            "food_name": self.food_name,
            "category": self.category,
            "serving_size": self.serving_size,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
        }


class FoodLog(db.Model):
    __tablename__ = "food_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)  # multiplier of `serving_size`
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast | lunch | dinner | snacks
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food = db.relationship("Food", lazy=True)

    @property
    def calories(self):
        return round(self.food.calories * self.quantity, 1)

    @property
    def protein(self):
        return round(self.food.protein * self.quantity, 1)

    @property
    def carbs(self):
        return round(self.food.carbs * self.quantity, 1)

    @property
    def fat(self):
        return round(self.food.fat * self.quantity, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "food_id": self.food_id,
            "food_name": self.food.food_name,
            "serving_size": self.food.serving_size,
            "quantity": self.quantity,
            "meal_type": self.meal_type,
            "date": self.date.isoformat(),
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
        }


class ExerciseLog(db.Model):
    __tablename__ = "exercise_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_type = db.Column(db.String(30), nullable=False)  # walking | running | cycling | gym_workout | yoga
    duration = db.Column(db.Integer, nullable=False)  # minutes
    calories_burned = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "exercise_type": self.exercise_type,
            "exercise_label": EXERCISE_LABELS.get(self.exercise_type, self.exercise_type),
            "duration": self.duration,
            "calories_burned": round(self.calories_burned, 1),
            "date": self.date.isoformat(),
        }


class WaterLog(db.Model):
    __tablename__ = "water_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # millilitres
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date.isoformat(),
        }


class WeightLog(db.Model):
    __tablename__ = "weight_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # kilograms
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "weight": self.weight,
            "date": self.date.isoformat(),
        }
