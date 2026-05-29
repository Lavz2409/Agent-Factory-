import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models import Base
from schemas import TodoCreate

# Configure test database
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Override the get_db dependency to use the test database
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="module")
async def client(setup_database):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_todo(client):
    todo_data = {"title": "Test Todo", "description": "This is a test todo"}
    response = await client.post("/todos/", json=todo_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo"

@pytest.mark.asyncio
async def test_read_todos(client):
    response = await client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_read_todo_by_id(client):
    # Create a todo to read
    todo_data = {"title": "Read Test Todo", "description": "Read this test todo"}
    create_response = await client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]

    # Read the created todo
    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read Test Todo"
    assert data["description"] == "Read this test todo"

@pytest.mark.asyncio
async def test_update_todo(client):
    # Create a todo to update
    todo_data = {"title": "Update Test Todo", "description": "Update this test todo"}
    create_response = await client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]

    # Update the created todo
    updated_data = {"title": "Updated Title", "description": "Updated description"}
    response = await client.put(f"/todos/{todo_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"

@pytest.mark.asyncio
async def test_delete_todo(client):
    # Create a todo to delete
    todo_data = {"title": "Delete Test Todo", "description": "Delete this test todo"}
    create_response = await client.post("/todos/", json=todo_data)
    todo_id = create_response.json()["id"]

    # Delete the created todo
    response = await client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

    # Verify deletion
    get_response = await client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404