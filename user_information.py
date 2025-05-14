import sqlite3
import hashlib
import re
from datetime import datetime
from typing import Optional, Tuple
from workout_status import WorkoutStatus

database = "database/health_tracker.db"

class UserInformation:
    def __init__(self, db_path: str = "database/health_tracker.db"):
        """Initialize the UserInformation class with optional database path."""
        self.database = db_path
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.create_user_table()
        self.workout_status = WorkoutStatus(self.cursor, self.conn)
        
    def create_user_table(self):  
        """ Create users table""" 
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                year_of_birth INTEGER, 
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def user_account(self, username: str, email: str, password: str, first_name: str, last_name: str, year_of_birth: int, gender: str) -> Tuple[bool, str]:
        """Register a new user with username, email, password, first name, last name, year of birth
           and check validation of username, email, and password. 
        Returns: (success, message) tuple.
        """
        # Validate username
        if not (3 <= len(username) <= 8):
            return False, "Your username must be between 3 and 8 characters."
        
        # Validate password length
        if len(password) < 8:
            return False, "Your password must be at least 8 characters long."
        
        # Validate email format
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            return False, "Invalid email address"
        
        # Validate year_of_birth
        if not (1945 <= year_of_birth <= 2012):
            return False, "Please enter a valid year of birth."
        
        if gender.lower() not in {"male", "female"}:
            return False, "Invalid input."
        
        try:
            password_hash = self._hash_password(password)
            
            self.cursor.execute(
                    "INSERT INTO users (username, email, password_hash, first_name, last_name, year_of_birth, gender) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (username, email, password_hash, first_name, last_name, year_of_birth, gender)
                )
            self.conn.commit()
                
            return True, "User registered successfully"
            
        except sqlite3.IntegrityError as e:
            if "users.username" in str(e):
                return False, "Username already exists"
            elif "users.email" in str(e):
                return False, "Email already exists"
            return False, "Database Error"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate a user with username and password.
        Returns:
            - (success, message) tuple.
        """
        password_hash = self._hash_password(password)
        self.cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = self.cursor.fetchone()
        if user:
            return True, "Login successful"
        return False, "Invalid username or password"


    def get_user_profile(self, username: str) -> Optional[dict]:
        """Retrieve user profile information.
        Returns:
            - None if user not found.
        """
        try:
            self.cursor.execute(
                    """SELECT id, username, email, first_name, last_name, year_of_birth, gender, created_at 
                    FROM users 
                    WHERE username = ?""", (username,)
                )
            result = self.cursor.fetchone()
                
            if result:
                current_year = datetime.now().year
                year_of_birth = result[5]
                age = current_year - year_of_birth if year_of_birth else None
                return {
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "first_name": result[3],
                    "last_name": result[4],
                    "year_of_birth": year_of_birth,
                    "gender": result[6],
                    "age": age,
                    "created_at": result[7]
                }
            return None
                
        except Exception as e:
            return None
        
    def update_workout_status(self, username: str, workout_days: int, duration: float) -> Tuple[bool, str]:
        return self.workout_status.add_or_update_workout(username, workout_days, duration)

    def get_workout_status(self, username: str) -> Optional[dict]:
         return self.workout_status.get_workout_status(username)

    def close(self):
        """ Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

