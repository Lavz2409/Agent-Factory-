import pytest
from task_manager import add_task, view_tasks, complete_task, delete_task, load_tasks, save_tasks

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Clear the tasks before each test
    save_tasks([])
    yield
    # Teardown: Clear the tasks after each test
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
    assert complete_task(task_id) is True
    tasks = view_tasks()
    assert tasks[0]['status'] == "Completed"

def test_complete_task_invalid_id():
    assert complete_task(999) is False

def test_delete_task():
    add_task("Test Task 1")
    tasks = view_tasks()
    task_id = tasks[0]['id']
    assert delete_task(task_id) is True
    tasks = view_tasks()
    assert len(tasks) == 0

def test_delete_task_invalid_id():
    assert delete_task(999) is False

def test_load_and_save_tasks():
    add_task("Test Task 1")
    add_task("Test Task 2")
    tasks_before = view_tasks()
    save_tasks(tasks_before)
    tasks_after = load_tasks()
    assert tasks_before == tasks_after