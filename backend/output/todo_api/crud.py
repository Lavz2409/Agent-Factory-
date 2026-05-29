from sqlalchemy.orm import Session
from models import Todo
from schemas import TodoCreate, TodoUpdate

def create_todo_in_db(db: Session, todo: TodoCreate) -> Todo:
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos_from_db(db: Session) -> list[Todo]:
    return db.query(Todo).all()

def get_todo_from_db(db: Session, todo_id: int) -> Todo:
    return db.query(Todo).filter(Todo.id == todo_id).first()

def update_todo_in_db(db: Session, todo_id: int, todo: TodoUpdate) -> Todo:
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        for key, value in todo.dict(exclude_unset=True).items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo_from_db(db: Session, todo_id: int) -> bool:
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False