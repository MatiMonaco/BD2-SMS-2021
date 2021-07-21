from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field



def ResponseModel(data, message):
    return {
        "data": data,
        "message": message,
    }

def PaginatedResponseModel(data, page, limit, total_pages, total):
    return {
        "data": data,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total": total
    }
