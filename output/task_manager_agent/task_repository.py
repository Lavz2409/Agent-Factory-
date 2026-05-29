import json
from typing import List, Dict

TASKS_FILE = 'tasks.json'

def load_tasks() -> List[Dict]:
    """Load tasks from a JSON file."""
    try:
        with open(TASKS_FILE, 'r') as file:
            tasks = json.load(file)
            if isinstance(tasks, list):
                return tasks
            else:
                return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to a JSON file."""
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)