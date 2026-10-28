from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=512)


class ProductOut(BaseModel):
    id: int
    name: str
    image_url: str
    created_at: datetime
