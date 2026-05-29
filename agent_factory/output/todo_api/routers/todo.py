from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sqlite3

from schemas import TodoCreate, TodoUpdate, TodoResponse
from database import get_db
from crud import get_todo_by_id, get_all_todos, create_todo, update_todo, delete_todo

router = APIRouter()

@router.post('/todos/', response_model=TodoResponse)
async def create_todo_route(todo: TodoCreate, db: sqlite3.Connection = Depends(get_db)) -> TodoResponse:
    db_todo = create_todo(db, 