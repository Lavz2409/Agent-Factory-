import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from api_service.main import app
from api_service.dependencies import get_db
from api_service.models import Base, Todo
from api_service.schemas import TodoCreate

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
async def client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_todo(client):
    todo_data = {"title": "Test Todo", "description": "Test Description"}
    response = await client.post("/todos/", json=todo_data)
    assert response.status_code == 200
    assert response.json()["title"] == todo_data["title"]