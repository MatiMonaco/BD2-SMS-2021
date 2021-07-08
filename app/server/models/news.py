from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class NewsSchema(BaseModel):
    Title: str = Field(...)
    Source: EmailStr = Field(...)
    URL: str = Field(...)
    Date: datetime = Field(...)
    Category: str = Field(...)
    Group: int = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@x.edu.ng",
                "course_of_study": "Water resources engineering",
                "year": 2,
                "gpa": "3.0",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
