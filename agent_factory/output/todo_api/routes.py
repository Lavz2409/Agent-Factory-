from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import UserCreate, UserLogin, TodoCreate, TodoUpdate, UserResponse, Todo
from services import create_user, authenticate_user, create_access_token, get_todos, create_todo, update_todo, delete_todo
from database import get_db
from dependencies import get_current_user

app = FastAPI()

@app.post('/register', response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user

@app.post('/login')
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.get('/todos', response_model=List[Todo])
def read_todos(token: str = Depends(get_current_user), db: Session = Depends(get_db)):
    todos = get_todos(db, token)
    return todos

@app.post('/todos', response_model=Todo)
def create_todo_item(todo_data: TodoCreate, token: str = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = create_todo(db, token, todo_data)
    return todo

@app.put('/todos/{todo_id}', response_model=Todo)
def update_todo_item(todo_id: int, todo_data: TodoUpdate, token: str = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = update_todo(db, token, todo_id, todo_data)
    return todo

@app.delete('/todos/{todo_id}')
def delete_todo_item(todo_id: int, token: str = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_todo(db, token, todo_id)
    return {"detail": "Todo deleted successfully"}