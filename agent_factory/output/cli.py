```
import click
from main import add_task, view_tasks, complete_task, delete_task

@click.group()
def cli():
    """Task Manager Agent CLI"""
    pass

@cli.command()
@click.argument('title')
def add(title):
    """Add a new task with the given TITLE."""
    try:
        add_task(title)
        click.echo(f"Task '{title}' added successfully.")
    except Exception as e:
        click.echo(f"Error adding task: {e}")

@cli.command()
def view():
    """View all tasks."""
    try:
        tasks = view_tasks()
        if tasks:
            for task in tasks:
                status = "Completed" if task['status'] else "Pending"
                click.echo(f"ID: {task['id']}, Title: {task['title']}, Status: {status}")
        else:
            click.echo("No tasks available.")
    except Exception as e:
        click.echo(f"Error viewing tasks: {e}")

@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark the task with the given TASK_ID as completed."""
    try:
        if complete_task(task_id):
            click.echo(f"Task ID {task_id} marked as completed.")
        else:
            click.echo(f"Task ID {task_id} not found.")
    except Exception as e:
        click.echo(f"Error completing task: {e}")

@cli.command()
@click.argument('task_id', type=int)
def delete(task_id):
    """Delete the task with the given TASK_ID."""
    try:
        if delete_task(task_id):
            click.echo(f"Task ID {task_id} deleted.")
        else:
            click.echo(f"Task ID {task_id} not found.")
    except Exception as e:
        click.echo(f"Error deleting task: {e}")

if __name__ == '__main__':
    cli()
```