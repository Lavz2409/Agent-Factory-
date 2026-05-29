import json
from typing import List, Dict

TASKS_FILE = 'tasks.json'

def load_tasks() -> List[Dict]:
    """Load tasks from a JSON file."""
    try:
        with open(TASKS_FILE, 'r') as file:
            tasks = json.load(file)
            return tasks
    except FileNotFoundError:
        # If the file does not exist, return an empty list
        return []
    except json.JSONDecodeError:
        # If the file is corrupted, also return an empty list
        return []

def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to a JSON file."""
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)