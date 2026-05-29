from sqlalchemy.orm import Session
from app import models, schemas

def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todo(db: Session, todo_id: int) -> models.Todo:
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def get_todos(db: Session, skip: int = 0, limit: int = 10) -> list[models.Todo]:
    return db.query(models.Todo).offset(skip).limit(limit).all()
