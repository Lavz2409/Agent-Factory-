import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
from models import Todo
from schemas import TodoCreate, TodoUpdate

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_create_todo():
    response = client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "This is a test todo item"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo item"
    assert "id" in data

def test_get_todos():
    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_todo():
    # First, create a todo to retrieve
    create_response = client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "This is a test todo item"}
    )
    todo_id = create_response.json()["id"]

    # Now, retrieve the created todo
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Test Todo"

def test_update_todo():
    # First, create a todo to update
    create_response = client.post(
        "/todos/",
        json={"title": "Old Title", "description": "Old description"}
    )
    todo_id = create_response.json()["id"]

    # Now, update the created todo
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "New Title", "description": "New description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New description"

def test_delete_todo():
    # First, create a todo to delete
    create_response = client.post(
        "/todos/",
        json={"title": "To be deleted", "description": "This will be deleted"}
    )
    todo_id = create_response.json()["id"]

    # Now, delete the created todo
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

    # Verify the todo is deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404