import sqlite3
from typing import Tuple, Optional

database = "database/health_tracker.db"

class PersonalRecord:
    def __init__(self, db_path: str = "database/health_tracker.db"):
        self.database = db_path
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.create_health_table()

    def create_health_table(self):
        """Create the health data table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.conn.commit()

    def _calculate_bmi(self, weight: float, height: float) -> float:
        """Calculate BMI using the formula: BMI = weight (kg) / height^2 (m^2)."""
        return round(weight / (height ** 2), 2)

    def _is_valid_measurement(self, value: float) -> bool:
        """Check if the input value is a valid positive number."""
        return isinstance(value, (int, float)) and value > 0

    def add_or_update_measurements(self, username: str, weight: float, height: float) -> Tuple[bool, str]:
        """Add or update user's health measurements with validation."""
        if not self._is_valid_measurement(weight):
            return False, "Invalid weight value. It must be a positive number."

        if not self._is_valid_measurement(height):
            return False, "Invalid height value. It must be a positive number."

        bmi = self._calculate_bmi(weight, height)

        try:
            self.cursor.execute("""
                SELECT id FROM health_data WHERE username = ?
            """, (username,))
            existing = self.cursor.fetchone()

            if existing:
                # Update record
                self.cursor.execute("""
                    UPDATE health_data
                    SET weight = ?, height = ?, bmi = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE username = ?
                """, (weight, height, bmi, username))
            else:
                # Insert new record
                self.cursor.execute("""
                    INSERT INTO health_data (username, weight, height, bmi)
                    VALUES (?, ?, ?, ?)
                """, (username, weight, height, bmi))

            self.conn.commit()
            return True, "Your information updated successfully."

        except Exception as e:
            return False, f"Failed to save health data: {str(e)}"

    def get_health_data(self, username: str) -> Optional[dict]:
        """Retrieve a user's health data."""
        self.cursor.execute("""
            SELECT weight, height, bmi, last_updated
            FROM health_data WHERE username = ?
        """, (username,))
        data = self.cursor.fetchone()
        if data:
            return {
                "weight in kg": data[0],
                "height in meters": data[1],
                "bmi": data[2],
                "last_updated": data[3]
            }
        return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
