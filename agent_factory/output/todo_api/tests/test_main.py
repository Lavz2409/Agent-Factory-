import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import TodoCreate, TodoUpdate

client = TestClient(app)

@pytest.fixture
def todo_data():
    return {"title": "Test Todo", "description": "Test Description"}

@pytest.fixture
def created_todo(todo_data):
    response = client.post("/todos/", json=todo_data)
    return response.json()

# Add more tests here
