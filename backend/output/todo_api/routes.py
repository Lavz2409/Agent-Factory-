from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, database
from .database import get_db

router = APIRouter()

@router.post("/todos/", response_model=schemas.TodoResponse)
async def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)) -> schemas.TodoResponse:
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.get("/todos/", response_model=List[schemas.TodoResponse])
async def get_todos(db: Session = Depends(get_db)) -> List[schemas.TodoResponse]:
    todos = db.query(models.Todo).all()
    return todos

@router.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
async def get_todo(todo_id: int, db: Session = Depends(get_db)) -> schemas.TodoResponse:
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)) -> schemas.TodoResponse:
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> None:
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()