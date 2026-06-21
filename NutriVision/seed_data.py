"""
Seeds the `foods` table with a starter database of common foods.

Run directly:  python seed_data.py
Or imported and called from app.py on first boot.
"""
from extensions import db
from models import Food

# (food_name, category, serving_size, calories, protein_g, carbs_g, fat_g)
FOODS = [
    # --- Fruits ---
    ("Banana", "Fruit", "1 medium (118g)", 105, 1.3, 27.0, 0.4),
    ("Apple", "Fruit", "1 medium (182g)", 95, 0.5, 25.0, 0.3),
    ("Orange", "Fruit", "1 medium (131g)", 62, 1.2, 15.4, 0.2),
    ("Strawberries", "Fruit", "1 cup (152g)", 49, 1.0, 11.7, 0.5),
    ("Blueberries", "Fruit", "1 cup (148g)", 84, 1.1, 21.4, 0.5),
    ("Grapes", "Fruit", "1 cup (151g)", 104, 1.1, 27.3, 0.2),
    ("Watermelon", "Fruit", "1 cup (152g)", 46, 0.9, 11.5, 0.2),
    ("Mango", "Fruit", "1 cup (165g)", 99, 1.4, 24.7, 0.6),
    ("Avocado", "Fruit", "1/2 medium (100g)", 160, 2.0, 8.5, 14.7),
    ("Pineapple", "Fruit", "1 cup (165g)", 82, 0.9, 21.6, 0.2),

    # --- Vegetables ---
    ("Broccoli", "Vegetable", "1 cup (91g)", 31, 2.5, 6.0, 0.3),
    ("Spinach (raw)", "Vegetable", "1 cup (30g)", 7, 0.9, 1.1, 0.1),
    ("Carrot", "Vegetable", "1 medium (61g)", 25, 0.6, 6.0, 0.1),
    ("Sweet Potato (baked)", "Vegetable", "1 medium (130g)", 112, 2.0, 26.0, 0.1),
    ("Potato (baked)", "Vegetable", "1 medium (173g)", 161, 4.3, 37.0, 0.2),
    ("Tomato", "Vegetable", "1 medium (123g)", 22, 1.1, 4.8, 0.2),
    ("Cucumber", "Vegetable", "1 cup (104g)", 16, 0.7, 3.8, 0.1),
    ("Bell Pepper", "Vegetable", "1 cup (149g)", 30, 1.0, 7.0, 0.3),
    ("Onion", "Vegetable", "1 medium (110g)", 44, 1.2, 10.3, 0.1),
    ("Cauliflower", "Vegetable", "1 cup (100g)", 25, 1.9, 5.0, 0.3),

    # --- Grains & Carbs ---
    ("White Rice (cooked)", "Grain", "1 cup (158g)", 205, 4.3, 45.0, 0.4),
    ("Brown Rice (cooked)", "Grain", "1 cup (195g)", 216, 5.0, 45.0, 1.8),
    ("Oats (cooked)", "Grain", "1 cup (234g)", 166, 5.9, 28.0, 3.6),
    ("Whole Wheat Bread", "Grain", "1 slice (28g)", 69, 3.6, 12.0, 1.0),
    ("White Bread", "Grain", "1 slice (25g)", 67, 2.0, 13.0, 0.8),
    ("Quinoa (cooked)", "Grain", "1 cup (185g)", 222, 8.1, 39.0, 3.6),
    ("Pasta (cooked)", "Grain", "1 cup (140g)", 221, 8.1, 43.0, 1.3),
    ("Bagel", "Grain", "1 medium (95g)", 245, 9.5, 48.0, 1.5),
    ("Tortilla (flour)", "Grain", "1 medium (49g)", 144, 3.9, 24.0, 3.5),
    ("Granola", "Grain", "1/2 cup (61g)", 298, 6.5, 32.7, 16.7),

    # --- Protein ---
    ("Chicken Breast (cooked)", "Protein", "100 g", 165, 31.0, 0.0, 3.6),
    ("Salmon (cooked)", "Protein", "100 g", 208, 20.0, 0.0, 13.0),
    ("Egg", "Protein", "1 large", 72, 6.3, 0.4, 4.8),
    ("Ground Beef 90% Lean (cooked)", "Protein", "100 g", 217, 26.0, 0.0, 12.0),
    ("Tofu", "Protein", "100 g", 76, 8.0, 1.9, 4.8),
    ("Shrimp (cooked)", "Protein", "100 g", 99, 24.0, 0.2, 0.3),
    ("Turkey Breast (cooked)", "Protein", "100 g", 135, 30.0, 0.0, 1.0),
    ("Tuna (canned in water)", "Protein", "100 g", 116, 26.0, 0.0, 0.8),
    ("Pork Chop (cooked)", "Protein", "100 g", 231, 25.0, 0.0, 14.0),
    ("Black Beans (cooked)", "Protein", "1 cup (172g)", 227, 15.2, 40.8, 0.9),

    # --- Dairy ---
    ("Whole Milk", "Dairy", "1 cup (244g)", 149, 7.7, 11.7, 8.0),
    ("Skim Milk", "Dairy", "1 cup (245g)", 83, 8.3, 12.2, 0.2),
    ("Greek Yogurt (plain)", "Dairy", "1 cup (245g)", 146, 25.0, 8.0, 4.0),
    ("Cheddar Cheese", "Dairy", "1 oz (28g)", 113, 7.0, 0.4, 9.3),
    ("Cottage Cheese", "Dairy", "1 cup (226g)", 222, 25.0, 9.0, 9.8),
    ("Butter", "Dairy", "1 tbsp (14g)", 102, 0.1, 0.0, 11.5),

    # --- Nuts, Seeds & Fats ---
    ("Almonds", "Nuts & Fats", "1 oz (28g)", 164, 6.0, 6.1, 14.2),
    ("Peanut Butter", "Nuts & Fats", "2 tbsp (32g)", 188, 8.0, 6.9, 16.0),
    ("Walnuts", "Nuts & Fats", "1 oz (28g)", 185, 4.3, 3.9, 18.5),
    ("Olive Oil", "Nuts & Fats", "1 tbsp (14g)", 119, 0.0, 0.0, 13.5),
    ("Chia Seeds", "Nuts & Fats", "1 oz (28g)", 138, 4.7, 12.0, 8.7),

    # --- Snacks & Misc ---
    ("Dark Chocolate (70%)", "Snack", "1 oz (28g)", 170, 2.2, 13.0, 12.0),
    ("Popcorn (air-popped)", "Snack", "1 cup (8g)", 31, 1.0, 6.2, 0.4),
    ("Potato Chips", "Snack", "1 oz (28g)", 152, 2.0, 15.0, 10.0),
    ("Hummus", "Snack", "2 tbsp (30g)", 70, 2.0, 6.0, 4.0),
    ("Protein Bar", "Snack", "1 bar (60g)", 220, 20.0, 23.0, 7.0),
    ("Whey Protein Shake", "Snack", "1 scoop (30g)", 120, 24.0, 3.0, 1.5),

    # --- Beverages ---
    ("Orange Juice", "Beverage", "1 cup (248g)", 112, 1.7, 25.8, 0.5),
    ("Black Coffee", "Beverage", "1 cup (240ml)", 2, 0.3, 0.0, 0.0),
    ("Green Tea", "Beverage", "1 cup (240ml)", 2, 0.5, 0.5, 0.0),
]


def seed_foods():
    """Insert the FOODS list if the table is currently empty."""
    if Food.query.count() > 0:
        print(f"Foods table already has {Food.query.count()} rows — skipping seed.")
        return

    for name, category, serving, cal, protein, carbs, fat in FOODS:
        db.session.add(
            Food(
                food_name=name,
                category=category,
                serving_size=serving,
                calories=cal,
                protein=protein,
                carbs=carbs,
                fat=fat,
            )
        )
    db.session.commit()
    print(f"Seeded {len(FOODS)} foods into the database.")


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        db.create_all()
        seed_foods()
