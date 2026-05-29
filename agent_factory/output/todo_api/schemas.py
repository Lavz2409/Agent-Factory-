from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    title: Optional[str] = None

class TodoInDBBase(TodoBase):
    id: int

    class Config:
        orm_mode = True

class Todo(TodoInDBBase):
    pass

class TodoInDB(TodoInDBBase):
    pass