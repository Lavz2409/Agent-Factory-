```
import pytest
from task_manager import add_task, view_tasks, complete_task, delete_task, load_tasks, save_tasks

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Ensure the tasks.json file is empty before each test
    save_tasks([])
    yield
    # Teardown: Clean up after each test
    save_tasks([])

def test_add_task():
    add_task("Test Task 1")
    tasks = view_tasks()
    assert len(tasks) == 1
    assert tasks[0]['title'] == "Test Task 1"
    assert tasks[0]['status'] == "Pending"

def test_view_tasks():
    add_task("Test Task 1")
    add_task("Test Task 2")
    tasks = view_tasks()
    assert len(tasks) == 2
    assert tasks[0]['title'] == "Test Task 1"
    assert tasks[1]['title'] == "Test Task 2"

def test_complete_task():
    add_task("Test Task 1")
    tasks = view_tasks()
    task_id = tasks[0]['id']
    result = complete_task(task_id)
    assert result is True
    tasks = view_tasks()
    assert tasks[0]['status'] == "Completed"

def test_complete_nonexistent_task():
    result = complete_task(999)
    assert result is False

def test_delete_task():
    add_task("Test Task 1")
    tasks = view_tasks()
    task_id = tasks[0]['id']
    result = delete_task(task_id)
    assert result is True
    tasks = view_tasks()
    assert len(tasks) == 0

def test_delete_nonexistent_task():
    result = delete_task(999)
    assert result is False
```