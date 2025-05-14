import os
import pytest
from user_information import UserInformation

TEST_DB_PATH = "test_health_tracker.db"

@pytest.fixture
def user_info():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    ui = UserInformation(db_path=TEST_DB_PATH)
    yield ui
    
    ui.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_user_table_creation(user_info):
    user_info.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    assert user_info.cursor.fetchone() is not None

def test_password_hashing(user_info):
    password = "password123456789"
    hashed = user_info._hash_password(password)
    assert len(hashed) == 64
    assert hashed != password
    assert user_info._hash_password(password) == hashed

def test_user_registration_success(user_info):
    result = user_info.user_account("John12", "john11@example.com", "password123", "John", "Thomas", 2000, "male")
    assert result[0] is True
    assert result[1] == "User registered successfully"

def test_invalid_gender(user_info):
    result = user_info.user_account("John12", "john11@example.com", "password123", "John", "Smith", 1990, "unknown")
    assert result[0] is False
    assert "Invalid input." in result[1]

def test_user_registration_username_validation(user_info):
    result = user_info.user_account("ab", "test@example.com", "password123", "John", "Thomas", 2000, "male")
    assert result[0] is False
    assert "between 3 and 8 characters" in result[1]

    result = user_info.user_account("abcdefghi", "abct@example.com", "password123", "John", "Thomas", 2000, "male")
    assert result[0] is False
    assert "between 3 and 8 characters" in result[1]

def test_user_registration_password_validation(user_info):
    result = user_info.user_account("John12", "John11t@example.com", "short", "John", "Thomas", 2000, "male")
    assert result[0] is False
    assert "at least 8 characters" in result[1]

def test_user_registration_email_validation(user_info):
    result = user_info.user_account("john", "invalid-email", "password123", "John", "Thomas", 2000, "male")
    assert result[0] is False
    assert "Invalid email address" in result[1]

def test_duplicate_username(user_info):
    user_info.user_account("john11", "john22@example.com", "password123", "John", "Thomas",2000, "male")
    result = user_info.user_account("john11", "jogh2@example.com", "password123", "John", "Thomas", 2000, "male")
    assert result[0] is False
    assert "Username already exists" in result[1]

def test_duplicate_email(user_info):
    user_info.user_account("jer1", "jer1@example.com", "password123", "John", "Thomas", 2000, "female")
    result = user_info.user_account("jer2", "jer1@example.com", "password123", "John", "Thomas", 2000, "female")
    assert result[0] is False
    assert "Email already exists" in result[1]

def test_user_birthday_validation(user_info):
    result = user_info.user_account("john", "john@example.com", "password123", "John", "Thomas", 1900, "male")
    assert result[0] is False
    assert "valid year of birth." in result[1]

def test_login_success(user_info):
    user_info.user_account("john", "john@example.com", "password123", "John", "Thomas", 2000, "male")
    result = user_info.login("john", "password123")
    assert result[0] is True
    assert result[1] == "Login successful"

def test_login_failure(user_info):
    user_info.user_account("john", "john@example.com", "password123", "John", "Thomas", 2000, "male")
    result = user_info.login("john", "wrongpassword")
    assert result[0] is False

    result = user_info.login("nonexistent", "password123")
    assert result[0] is False

def test_get_user_profile(user_info):
    user_info.user_account("testusr", "test@example.com", "password123", "John", "Thomas", 2000, "male")
    profile = user_info.get_user_profile("testusr")
    assert profile is not None
    assert profile["username"] == "testusr"
    assert profile["email"] == "test@example.com"
    assert profile["first_name"] == "John"
    assert profile["last_name"] == "Thomas"
    assert profile["year_of_birth"] == 2000
    assert profile["gender"] == "male"
    assert "created_at" in profile
    assert "age" in profile

def test_get_nonexistent_user_profile(user_info):
    profile = user_info.get_user_profile("nonexistent")
    assert profile is None

def test_add_workout_status(user_info):
    user_info.user_account("John", "john@example.com", "password123", "John", "Thomas", 2000, "male")
    success, message = user_info.update_workout_status("john", 4, 1.5)
    assert success is True
    assert message == "Workout status updated successfully."

def test_get_workout_status(user_info):
    user_info.user_account("John", "john@example.com", "password123", "John", "Thomas", 2000, "male")
    user_info.update_workout_status("John", 4, 1.5)
    status = user_info.get_workout_status("John")
    assert status is not None
    assert status["Workout days per week"] == 4
    assert status["Average duration per day (hrs)"] == 1.5
    assert "Last updated" in status

def test_get_workout_status_nonexistent_user(user_info):
    status = user_info.get_workout_status("ghost")
    assert status is None
