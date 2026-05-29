import sys
import json
from pathlib import Path

TASKS_FILE = Path("tasks.json")

def load_tasks():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)

def add_task(title):
    tasks = load_tasks()
    task_id = len(tasks) + 1
    tasks.append({"id": task_id, "title": title, "status": "Pending"})
    save_tasks(tasks)
    print(f"Task added: {title}")

def view_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks available.")
        return
    for task in tasks:
        print(f"[{task['id']}] {task['title']} - {task['status']}")

def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = "Completed"
            save_tasks(tasks)
            print(f"Task {task_id} marked as completed.")
            return
    print(f"Task with ID {task_id} not found.")

def delete_task(task_id):
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            tasks.pop(i)
            save_tasks(tasks)
            print(f"Task {task_id} deleted.")
            return
    print(f"Task with ID {task_id} not found.")

def main():
    while True:
        command = input("Enter command (add/view/complete/delete/exit): ").strip().lower()
        if command == "exit":
            print("Exiting Task Manager.")
            break
        elif command.startswith("add "):
            _, title = command.split(" ", 1)
            add_task(title)
        elif command == "view":
            view_tasks()
        elif command.startswith("complete "):
            try:
                _, task_id = command.split(" ", 1)
                complete_task(int(task_id))
            except ValueError:
                print("Invalid task ID.")
        elif command.startswith("delete "):
            try:
                _, task_id = command.split(" ", 1)
                delete_task(int(task_id))
            except ValueError:
                print("Invalid task ID.")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()