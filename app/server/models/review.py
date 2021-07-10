from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReviewSchema(BaseModel):
    reviewer: str = Field(...)
    score: float = Field(..., ge=0, le=5)
    comment: str = Field(...)
    created_at: datetime = Field(...)