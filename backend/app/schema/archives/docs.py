from pydantic import BaseModel, Field, conlist, ValidationError
from typing import Optional, List

EMBEDDING_DIM = 1536
Vector = conlist(float, min_length=EMBEDDING_DIM, max_length=EMBEDDING_DIM)

class Doc(BaseModel):
    doc_id: Optional[int] = Field(default=None) # primary key, automatically asigned
    api_key: str
    title: str
    tags: List[str]

    class Config:
        from_attributes = True

class Chunk(BaseModel):
    chunk_id: str # primary_key, needs to be explicxitly given
    api_key: str
    doc_id: str
    text: str
    embeddings: List[float]

    class Config:
        from_attributes = True

"""
# TODO: Add support for index_id and namespace_id.
"""
class textMetadata(BaseModel):
    api_key: str
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    index_id: Optional[str] = Field(default=None)
    namespace_id: Optional[str] = Field(default=None)

    class Config:
        from_attributes = True
