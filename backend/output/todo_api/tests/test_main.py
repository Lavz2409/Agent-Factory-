import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def create_todo():
    response = client.post("/todos/", json={"title": "Test Todo", "description": "Test Description"})
    return response.json()

def test_create_todo(create_todo):
    assert create_todo["title"] == "Test Todo"
    assert create_todo["description"] == "Test Description"

def test_get_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_todo(create_todo):
    todo_id = create_todo["id"]
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

def test_update_todo(create_todo):
    todo_id = create_todo["id"]
    response = client.put(f"/todos/{todo_id}", json={"title": "Updated Todo", "description": "Updated Description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Todo"

def test_delete_todo(create_todo):
    todo_id = create_todo["id"]
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    assert client.get(f"/todos/{todo_id}").status_code == 404