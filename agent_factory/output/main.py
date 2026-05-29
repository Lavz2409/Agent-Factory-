```
import click
import json
import os

TASKS_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as file:
        return json.load(file)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)

def add_task(title):
    tasks = load_tasks()
    task_id = len(tasks) + 1
    tasks.append({"id": task_id, "title": title, "status": "Pending"})
    save_tasks(tasks)
    click.echo(f"Task '{title}' added with ID {task_id}.")

def view_tasks():
    tasks = load_tasks()
    if not tasks:
        click.echo("No tasks available.")
        return
    for task in tasks:
        status = task['status']
        click.echo(f"[{task['id']}] {task['title']} - {status}")

def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'Completed'
            save_tasks(tasks)
            click.echo(f"Task ID {task_id} marked as completed.")
            return
    click.echo(f"Task ID {task_id} not found.")

def delete_task(task_id):
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            del tasks[i]
            save_tasks(tasks)
            click.echo(f"Task ID {task_id} deleted.")
            return
    click.echo(f"Task ID {task_id} not found.")

@click.group()
def cli():
    pass

@cli.command()
@click.argument('title')
def add(title):
    """Add a new task with the given TITLE."""
    add_task(title)

@cli.command()
def view():
    """View all tasks."""
    view_tasks()

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark the task with TASK_ID as completed."""
    complete_task(task_id)

@cli.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Delete the task with TASK_ID."""
    delete_task(task_id)

if __name__ == '__main__':
    cli()
```