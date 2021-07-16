from typing import Optional, List
from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    name: str = Field(...)
    avatar_url: str = Field(...)
    bio: str = Field(...)
    languages: List[str] = Field(...)
    following: int = Field(..., ge=0) 
    followers: int = Field(..., ge=0)
    html_url: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "avatar_url": "https://avatars.githubusercontent.com/u/123455?v=4",
                "bio": "Short description",
                "languages": ["python", "java", "c"],
                "following": 10,
                "followers": 0,
                "html_url": "https://github.com/johndoe"
            }
        }

class UpdateUserModel(BaseModel):
    name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    languages: List[str]
    following: Optional[int]
    followers: Optional[int]
    html_url: Optional[str]
