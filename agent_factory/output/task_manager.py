```
import json
from typing import List, Dict

TASKS_FILE = 'tasks.json'

def load_tasks() -> List[Dict]:
    """Load tasks from the JSON file."""
    try:
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)

def add_task(title: str) -> None:
    """Add a new task with the given title."""
    tasks = load_tasks()
    task_id = len(tasks) + 1
    new_task = {
        "id": task_id,
        "title": title,
        "status": "Pending"
    }
    tasks.append(new_task)
    save_tasks(tasks)

def view_tasks() -> List[Dict]:
    """Return a list of all tasks."""
    return load_tasks()

def complete_task(task_id: int) -> bool:
    """Mark a task as completed."""
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'Completed'
            save_tasks(tasks)
            return True
    return False

def delete_task(task_id: int) -> bool:
    """Delete a task by its ID."""
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            del tasks[i]
            save_tasks(tasks)
            return True
    return False
```