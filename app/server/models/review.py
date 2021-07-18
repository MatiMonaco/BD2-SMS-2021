from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReviewSchema(BaseModel):
    reviewer: str = Field(...)
    repo_name: str = Field(..., regex="^[a-zA-Z]+/[a-zA-Z_-]+$")
    score: float = Field(..., ge=0, le=5)
    comment: str = Field(...)
    # created_at: datetime = Field(...)

class UpdateReviewModel(BaseModel):
    score: Optional[int] = Field(..., ge=0, le=5)
    comment: Optional[str]

