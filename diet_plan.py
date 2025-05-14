import requests
import sys
import random
from goals import Goals

CATEGORIES = ['Beef', 'Chicken', 'Seafood', 'Vegetarian', 'Vegan', 'Pasta']

def get_calorie_goal_from_user(username: str) -> int:
    goals = Goals()
    try:
        goals.cursor.execute("SELECT calorie_intake FROM user_goals WHERE username = ?", (username,))
        result = goals.cursor.fetchone()
        if result:
            calorie_intake = int(result[0])
            print(f"Calorie goal for {username}: {calorie_intake} kcal/day")
            return calorie_intake
        else:
            print("No calorie goal found for this user. Please set up your goal first.")
            sys.exit(1)
    finally:
        goals.close()

def fetch_meals_by_category(category: str):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('meals', [])
    except requests.RequestException as e:
        print(f"Failed to fetch meals from {category}: {e}")
        return []

def get_random_meal(exclude_ids):
    attempts = 0
    while attempts < 10:
        category = random.choice(CATEGORIES)
        meals = fetch_meals_by_category(category)
        if meals:
            random.shuffle(meals)
            for meal in meals:
                if meal['idMeal'] not in exclude_ids:
                    return category, meal['strMeal'], meal['strMealThumb'], meal['idMeal']
        attempts += 1
    return None

def get_weekly_meal_plan():
    weekly_plan = []
    used_ids = set()
    for _ in range(7):  # for each day
        day_meals = []
        for _ in range(3):  # breakfast, lunch, dinner
            meal = get_random_meal(used_ids)
            if meal:
                category, name, image, meal_id = meal
                used_ids.add(meal_id)
                day_meals.append((category, name, image))
        weekly_plan.append(day_meals)
    return weekly_plan

def display_meal_plan(weekly_plan, calorie_goal):
    print(f"\nHere is your 7-day meal plan based on a daily goal of {calorie_goal} kcal:\n")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_times = ["Breakfast", "Lunch", "Dinner"]

    for day_name, meals in zip(days, weekly_plan):
        print(f"{day_name}:")
        for time, (category, name, image) in zip(meal_times, meals):
            print(f"  {time}: {name} (Category: {category})")
            print(f"    Image: {image}")
        print("-" * 60)

def generate_and_display_meal_plan(username: str):
    calorie_goal = get_calorie_goal_from_user(username)
    weekly_meals = get_weekly_meal_plan()
    display_meal_plan(weekly_meals, calorie_goal)

