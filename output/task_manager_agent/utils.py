from typing import List, Dict

def validate_task_id(task_id: int, tasks: List[Dict]) -> bool:
    """
    Validates if the given task_id exists in the list of tasks.

    Args:
        task_id (int): The ID of the task to validate.
        tasks (List[Dict]): The list of tasks.

    Returns:
        bool: True if the task_id is valid, False otherwise.
    """
    return any(task['ID'] == task_id for task in tasks)

def handle_invalid_input(message: str) -> None:
    """
    Handles invalid input by printing an error message.

    Args:
        message (str): The error message to display.
    """
    print(f"Error: {message}")

def handle_missing_task(task_id: int) -> None:
    """
    Handles the case where a task with the given ID does not exist.

    Args:
        task_id (int): The ID of the missing task.
    """
    print(f"Error: Task with ID {task_id} does not exist.")