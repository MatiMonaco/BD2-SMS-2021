from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReviewSchema(BaseModel):
    reviewer: str = Field(...)
    repo_name: str = Field(..., regex="^[0-9a-zA-Z]+/[0-9a-zA-Z_-]+$")
    score: float = Field(..., ge=0, le=5)
    comment: str = Field(...)
    # created_at: datetime = Field(...)

class UpdateReviewModel(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=5)
    comment: Optional[str]

