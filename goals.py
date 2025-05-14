from typing import Tuple, Optional
from user_information import UserInformation
from personal_record import PersonalRecord 
import sqlite3

database = "database/health_tracker.db"

class Goals:
    def __init__(self, db_path: str = "database/health_tracker.db"):
        self.database = db_path
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.user_info = UserInformation()
        self.health_record = PersonalRecord()
        self.create_goals_table()

    def create_goals_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                goal TEXT NOT NULL,
                bmr REAL NOT NULL,
                calorie_intake REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.conn.commit()

    def get_bmr(self, gender: str, weight: float, height: float, age: int) -> float:
        """Calculate BMR using Mifflin-St Jeor Equation."""
        if gender.lower() == "male":
            return 10 * weight + 6.25 * height - 5 * age + 5
        elif gender.lower() == "female":
            return 10 * weight + 6.25 * height - 5 * age - 161

    def get_activity_multiplier(self, days: int, duration: float) -> float:
        """Return multiplier based on workout frequency."""
        total_minutes = days * duration * 60

        if total_minutes == 0:
            return 1.2  # sedentary
        elif total_minutes <= 150:
            return 1.375  # light
        elif total_minutes <= 300:
            return 1.55  # moderate
        elif total_minutes <= 450:
            return 1.725  # very active
        else:
            return 1.9  # extra active

    def set_calorie_goal(self, username: str, goal: str) -> Tuple[bool, Optional[str]]:
        profile = self.user_info.get_user_profile(username)
        health_data = self.health_record.get_health_data(username)
        workout_data = self.user_info.get_workout_status(username)

        if not profile or not health_data:
            return False, "Missing user or health information."

        gender = profile.get("gender")
        age = profile.get("age")
        weight = health_data.get("weight in kg")  
        height = health_data.get("height in meters") * 100

        if not all([gender, age, weight, height]):
            return False, "Incomplete data for BMR calculation."

        bmr = self.get_bmr(gender, weight, height, age)

        # Workout data 
        workout_days = workout_data.get("Workout days per week", 0) if workout_data else 0
        duration = workout_data.get("Average duration per day (hrs)", 0) if workout_data else 0

        activity_multiplier = self.get_activity_multiplier(workout_days, duration)
        maintenance_calories = bmr * activity_multiplier

        # Adjust calories based on goal
        goal = goal.lower()
        if goal == "maintain":
            adjusted_calories = round(maintenance_calories)
        elif goal == "lose":
            adjusted_calories = round(maintenance_calories - 500)
        elif goal == "gain":
            adjusted_calories = round(maintenance_calories + 500)
        else:
            return False, "Invalid goal. Choose from 'maintain', 'lose', or 'gain'."

        try:
            self.cursor.execute("SELECT id FROM user_goals WHERE username = ?", (username,))
            existing = self.cursor.fetchone()

            if existing:
                self.cursor.execute("""
                    UPDATE user_goals
                    SET goal = ?, bmr = ?, calorie_intake = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE username = ?
                """, (goal, bmr, adjusted_calories, username))
            else:
                self.cursor.execute("""
                    INSERT INTO user_goals (username, goal, bmr, calorie_intake)
                    VALUES (?, ?, ?, ?)
                """, (username, goal, bmr, adjusted_calories))

            self.conn.commit()
            return True, f"Your estimated daily calorie intake to {goal} weight is {round(adjusted_calories)} kcal."

        except Exception as e:
            return False, f"Error saving goal: {e}"
        
    def get_goals(self, username: str) -> Optional[dict]:
        """Retrieve a user's goals."""
        self.cursor.execute("""
            SELECT goal, bmr, calorie_intake, last_updated
            FROM user_goals WHERE username = ?
        """, (username,))
        data = self.cursor.fetchone()
        if data:
            return {
                "goal": data[0],
                "bmr": data[1],
                "calorie intake": data[2],
                "last_updated": data[3]
            }
        return None

    def close(self):
        self.user_info.close()
        self.health_record.close()
        if self.conn:
            self.conn.close()
            self.conn = None

