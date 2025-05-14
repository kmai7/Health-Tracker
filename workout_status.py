from typing import Tuple, Optional

class WorkoutStatus:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn
        self.create_workout_table()

    def create_workout_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                workout_days_per_week INTEGER NOT NULL,
                duration_per_day REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.conn.commit()

    def add_or_update_workout(self, username: str, workout_days: int, duration_per_day: float) -> Tuple[bool, str]:
        if not (0 <= workout_days <= 7 and duration_per_day > 0):
            return False, "Workout days must be 0-7 and duration must be a positive number."

        try:
            self.cursor.execute("SELECT id FROM workout_status WHERE username = ?", (username,))
            existing = self.cursor.fetchone()

            if existing:
                self.cursor.execute("""
                    UPDATE workout_status
                    SET workout_days_per_week = ?, duration_per_day = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE username = ?
                """, (workout_days, duration_per_day, username))
            else:
                self.cursor.execute("""
                    INSERT INTO workout_status (username, workout_days_per_week, duration_per_day)
                    VALUES (?, ?, ?)
                """, (username, workout_days, duration_per_day))

            self.conn.commit()
            return True, "Workout status updated successfully."
        
        except Exception as e:
            return False, f"Error: {e}"

    def get_workout_status(self, username: str) -> Optional[dict]:
        self.cursor.execute("""
            SELECT workout_days_per_week, duration_per_day, last_updated
            FROM workout_status WHERE username = ?
        """, (username,))
        result = self.cursor.fetchone()
        if result:
            return {
                "Workout days per week": result[0],
                "Average duration per day (hrs)": result[1],
                "Last updated": result[2]
            }
        return None