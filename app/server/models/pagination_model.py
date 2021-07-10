from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class PaginationModel(BaseModel):
    data = Field(...)
    page: int = Field(...)
    limit: int = Field(...)
    total_pages: int = Field(...)

    def __init__(self,data,page,limit,total_pages):
        self.data = data
        self.page = page
        self.limit = limit
        self.total_pages = total_pages