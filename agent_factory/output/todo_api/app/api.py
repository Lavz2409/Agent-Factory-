from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter()

@router.get("/todos/", response_model=List[schemas.Todo])
def get_todos(db: Session = Depends(get_db)):
    todos = crud.get_todos(db)
    return todos

@router.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db=db, todo=todo)
