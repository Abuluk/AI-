from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FeedbackCreate(BaseModel):
    content: str

class FeedbackInDB(BaseModel):
    id: int
    user_id: int
    content: str
    status: str
    created_at: datetime
    solved_at: Optional[datetime]
    class Config:
        from_attributes = True

class FeedbackUpdate(BaseModel):
    status: Optional[str] 