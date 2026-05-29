import pytest
import json
import os
from task_storage import load_tasks, save_tasks

TEST_FILE = 'test_tasks.json'

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: create a test file
    with open(TEST_FILE, 'w') as f:
        json.dump([], f)
    yield
    # Teardown: remove the test file
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_load_tasks_empty():
    tasks = load_tasks()
    assert tasks == []

def test_save_tasks():
    tasks = [
        {"id": 1, "title": "Test Task 1", "status": "Pending"},
        {"id": 2, "title": "Test Task 2", "status": "Completed"}
    ]
    save_tasks(tasks)
    with open(TEST_FILE, 'r') as f:
        loaded_tasks = json.load(f)
    assert loaded_tasks == tasks

def test_load_tasks_with_data():
    tasks = [
        {"id": 1, "title": "Test Task 1", "status": "Pending"},
        {"id": 2, "title": "Test Task 2", "status": "Completed"}
    ]
    with open(TEST_FILE, 'w') as f:
        json.dump(tasks, f)
    loaded_tasks = load_tasks()
    assert loaded_tasks == tasks