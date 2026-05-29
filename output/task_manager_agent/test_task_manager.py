import unittest
from unittest.mock import patch, mock_open
from task_logic import add_task, view_tasks, complete_task, delete_task, load_tasks, save_tasks

class TestTaskManager(unittest.TestCase):

    @patch('task_logic.load_tasks', return_value=[])
    @patch('task_logic.save_tasks')
    def test_add_task(self, mock_save_tasks, mock_load_tasks):
        add_task("Buy groceries")
        tasks = view_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], "Buy groceries")
        self.assertEqual(tasks[0]['status'], "Pending")
        mock_save_tasks.assert_called_once()

    @patch('task_logic.load_tasks', return_value=[
        {'id': 1, 'title': 'Buy groceries', 'status': 'Pending'}
    ])
    @patch('task_logic.save_tasks')
    def test_view_tasks(self, mock_save_tasks, mock_load_tasks):
        tasks = view_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], "Buy groceries")
        self.assertEqual(tasks[0]['status'], "Pending")

    @patch('task_logic.load_tasks', return_value=[
        {'id': 1, 'title': 'Buy groceries', 'status': 'Pending'}
    ])
    @patch('task_logic.save_tasks')
    def test_complete_task(self, mock_save_tasks, mock_load_tasks):
        result = complete_task(1)
        tasks = view_tasks()
        self.assertTrue(result)
        self.assertEqual(tasks[0]['status'], "Completed")
        mock_save_tasks.assert_called_once()

    @patch('task_logic.load_tasks', return_value=[
        {'id': 1, 'title': 'Buy groceries', 'status': 'Pending'}
    ])
    @patch('task_logic.save_tasks')
    def test_delete_task(self, mock_save_tasks, mock_load_tasks):
        result = delete_task(1)
        tasks = view_tasks()
        self.assertTrue(result)
        self.assertEqual(len(tasks), 0)
        mock_save_tasks.assert_called_once()

    @patch('task_logic.load_tasks', return_value=[
        {'id': 1, 'title': 'Buy groceries', 'status': 'Pending'}
    ])
    @patch('task_logic.save_tasks')
    def test_complete_nonexistent_task(self, mock_save_tasks, mock_load_tasks):
        result = complete_task(2)
        self.assertFalse(result)
        mock_save_tasks.assert_not_called()

    @patch('task_logic.load_tasks', return_value=[
        {'id': 1, 'title': 'Buy groceries', 'status': 'Pending'}
    ])
    @patch('task_logic.save_tasks')
    def test_delete_nonexistent_task(self, mock_save_tasks, mock_load_tasks):
        result = delete_task(2)
        self.assertFalse(result)
        mock_save_tasks.assert_not_called()

if __name__ == '__main__':
    unittest.main()