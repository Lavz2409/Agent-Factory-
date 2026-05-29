import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Base, User, Todo
from database import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables in the database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_create_user(db_session):
    new_user = User(username="testuser", email="testuser@example.com")
    db_session.add(new_user)
    db_session.commit()

    user_in_db = db_session.query(User).filter(User.username == "testuser").first()
    assert user_in_db is not None
    assert user_in_db.email == "testuser@example.com"

def test_create_todo_with_user(db_session):
    new_user = User(username="testuser", email="testuser@example.com")
    db_session.add(new_user)
    db_session.commit()

    new_todo = Todo(title="Test Todo", description="Test Description", user_id=new_user.id)
    db_session.add(new_todo)
    db_session.commit()

    todo_in_db = db_session.query(Todo).filter(Todo.title == "Test Todo").first()
    assert todo_in_db is not None
    assert todo_in_db.description == "Test Description"
    assert todo_in_db.user_id == new_user.id

def test_user_email_unique_constraint(db_session):
    user1 = User(username="user1", email="duplicate@example.com")
    user2 = User(username="user2", email="duplicate@example.com")
    db_session.add(user1)
    db_session.commit()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_todo_user_relationship(db_session):
    new_user = User(username="testuser", email="testuser@example.com")
    db_session.add(new_user)
    db_session.commit()

    new_todo = Todo(title="Test Todo", description="Test Description", user_id=new_user.id)
    db_session.add(new_todo)
    db_session.commit()

    user_in_db = db_session.query(User).filter(User.id == new_user.id).first()
    assert len(user_in_db.todos) == 1
    assert user_in_db.todos[0].title == "Test Todo"