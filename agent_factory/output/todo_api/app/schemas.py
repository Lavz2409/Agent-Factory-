from pydantic import BaseModel, Field
from typing import Optional

class TodoBase(BaseModel):
    title: str = Field(..., example="Buy groceries")
    description: Optional[str] = Field(None, example="Milk, Bread, Cheese")

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    title: Optional[str] = None
    description: Optional[str] = None

class TodoInDBBase(TodoBase):
    id: int

    class Config:
        orm_mode = True

class Todo(TodoInDBBase):
    pass

class TodoInDB(TodoInDBBase):
    pass
