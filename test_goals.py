import pytest 
from goals import Goals
import sqlite3
import os

class MockUserInformation:
    def __init__(self):
        pass

    def get_user_profile(self, username):
        if username == "john":
            return {
                "gender": "male",
                "age": 25
            }
        return None

    def get_workout_status(self, username):
        if username == "john":
            return {
                "Workout days per week": 3,
                "Average duration per day (hrs)": 1
            }
        return None

    def close(self):
        pass


class MockPersonalRecord:
    def __init__(self):
        pass

    def get_health_data(self, username):
        if username == "john":
            return {
                "weight in kg": 70,
                "height in meters": 1.75
            }
        return None

    def close(self):
        pass

@pytest.fixture
def test_db():
    db_path = ":memory:"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            goal TEXT NOT NULL,
            bmr REAL NOT NULL,
            calorie_intake REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    yield conn, cursor
    conn.close()

@pytest.fixture
def goals(test_db):
    conn, cursor = test_db
    g = Goals()
    g.conn = conn
    g.cursor = cursor
    g.user_info = MockUserInformation()
    g.health_record = MockPersonalRecord()
    return g

def test_get_bmr_male(goals):
    bmr = goals.get_bmr("male", 70, 175, 25)
    expected_bmr = 10 * 70 + 6.25 * 175 - 5 * 25 + 5
    assert bmr == expected_bmr

def test_get_bmr_female(goals):
    bmr = goals.get_bmr("female", 60, 165, 30)
    expected_bmr = 10 * 60 + 6.25 * 165 - 5 * 30 - 161
    assert bmr == expected_bmr

def test_get_activity_multiplier_sedentary(goals):
    multiplier = goals.get_activity_multiplier(0, 0)
    assert multiplier == 1.2

def test_get_activity_multiplier_light(goals):
    multiplier = goals.get_activity_multiplier(3, 0.5)
    assert multiplier == 1.375

def test_get_activity_multiplier_moderate(goals):
    multiplier = goals.get_activity_multiplier(3, 1.5)
    assert multiplier == 1.55

def test_get_activity_multiplier_very_active(goals):
    multiplier = goals.get_activity_multiplier(5, 1.5)
    assert multiplier == 1.725

def test_get_activity_multiplier_extra_active(goals):
    multiplier = goals.get_activity_multiplier(6, 2)
    assert multiplier == 1.9

def test_calorie_goal_maintain(goals):
    success, message = goals.set_calorie_goal("john", "maintain")
    assert success is True
    assert "Your estimated daily calorie intake to maintain weight is" in message
    
    goals.cursor.execute("SELECT goal, bmr, calorie_intake FROM user_goals WHERE username = ?", ("john",))
    result = goals.cursor.fetchone()
    assert result is not None
    assert result[0] == "maintain"

def test_calorie_goal_lose(goals):
    success, message = goals.set_calorie_goal("john", "lose")
    assert success is True
    assert "to lose weight" in message
    
    goals.cursor.execute("SELECT goal, bmr, calorie_intake FROM user_goals WHERE username = ?", ("john",))
    result = goals.cursor.fetchone()
    assert result is not None
    assert result[0] == "lose"

def test_calorie_goal_gain(goals):
    success, message = goals.set_calorie_goal("john", "gain")
    assert success is True
    assert "to gain weight" in message
    
    goals.cursor.execute("SELECT goal, bmr, calorie_intake FROM user_goals WHERE username = ?", ("john",))
    result = goals.cursor.fetchone()
    assert result is not None
    assert result[0] == "gain"

def test_calorie_goal_invalid_goal(goals):
    success, message = goals.set_calorie_goal("john", "bulk")
    assert success is False
    assert "Invalid goal" in message

def test_missing_profile(goals):
    success, message = goals.set_calorie_goal("ghost", "maintain")
    assert success is False
    assert "Missing user or health information." in message

