import os
import sqlite3
import pytest
from personal_record import PersonalRecord

TEST_DB = "test_health_tracker.db"

@pytest.fixture
def record():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    pr = PersonalRecord()
    pr.conn = sqlite3.connect(TEST_DB)
    pr.cursor = pr.conn.cursor()
    pr.create_health_table()
    yield pr

    pr.conn.close()
    os.remove(TEST_DB)

def test_table_creation(record):
    record.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='health_data'")
    assert record.cursor.fetchone() is not None

def test_bmi_calculation(record):
    bmi = record._calculate_bmi(70, 1.75)  # 70kg, 1.75m
    assert round(bmi, 2) == 22.86

def test_invalid_weight_and_height(record):
    result = record.add_or_update_measurements("John", -50, 1.7)
    assert result[0] is False
    assert "Invalid weight" in result[1]

    result = record.add_or_update_measurements("John", 70, 0)
    assert result[0] is False
    assert "Invalid height" in result[1]

def test_insert_health_data(record):
    result = record.add_or_update_measurements("John", 65, 1.7)
    assert result[0] is True
    assert "updated successfully" in result[1]

    data = record.get_health_data("John")
    assert data is not None
    assert round(data["bmi"], 2) == round(65 / (1.7 ** 2), 2)

def test_update_health_data(record):
    record.add_or_update_measurements("testuser", 60, 1.7)
    record.add_or_update_measurements("testuser", 68, 1.7)
    data = record.get_health_data("testuser")
    assert round(data["weight in kg"], 2) == 68
    assert round(data["bmi"], 2) == round(68 / (1.7 ** 2), 2)

def test_get_health_data_for_nonexistent_user(record):
    data = record.get_health_data("nonexistent")
    assert data is None