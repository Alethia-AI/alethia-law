from pydantic import BaseModel, Field, conlist, ValidationError
from typing import Optional, List


class Image(BaseModel):
    image_id: Optional[int] = Field(default=None) # primary key, automatically asigned
    api_key: str
    url: str
    image: str
    embeddings: List[float]

    class Config:
        from_attributes = True


class Pixel(BaseModel):
    pixel_id: Optional[int] = Field(default=None) # primary key, automatically asigned
    api_key: str
    image_id: str
    embedding: List[float]

    class Config:
        from_attributes = True

class imageSchema(BaseModel):
    image_id: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None)
    text: Optional[str] = Field(default=None)
    image_url: str

    class Config:
        from_attributes = True