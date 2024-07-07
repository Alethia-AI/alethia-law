from pydantic import BaseModel, Field, conlist, ValidationError
from typing import Optional, List
from datetime import datetime, date

EMBEDDING_DIM = 1536
Vector = conlist(float, min_length=EMBEDDING_DIM, max_length=EMBEDDING_DIM)

class Case(BaseModel):
    case_id: Optional[int] = Field(default=None) # primary key, automatically asigned
    api_key: str
    case_name: str
    case_date: date
    case_source: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True

class Page(BaseModel):
    page_id: str # primary_key, needs to be explicxitly given
    api_key: str
    case_id: str
    text: str
    section_type: str
    page_number: int
    is_binding: bool
    concurring_voice: Optional[str] = Field(default=None)
    dissenting_voice: Optional[str] = Field(default=None)
    embeddings: List[float]

    class Config:
        from_attributes = True

class CreatePage(BaseModel):
    text: str
    section_type: str
    page_number: int
    is_binding: bool
    concurring_voice: Optional[str] = Field(default=None)
    dissenting_voice: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True
