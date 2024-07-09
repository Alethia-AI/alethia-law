from typing_extensions import Unpack
from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field
from typing import List, Optional

from datetime import date

class addQuery(BaseModel):
    query: str
    api_key: str
    query_level: int # 0 for web search, 1 for image search
    max_results: Optional[int] = Field(default=10)

    class Config:
        from_attributes = True

class query(BaseModel):
    query_id: Optional[int] = Field(default=None) # Primary key; set by the database
    query: str
    api_key: str
    query_level: int # 0 for web search, 1 for image search
    index_id: Optional[str] = Field(default=None)
    namespace_id: Optional[str] = Field(default=None)
    archive_id: Optional[str] = Field(default=None)
    use_cache: Optional[bool] = Field(default=True)
    max_results: int = Field(default=10)

    class Config:
        from_attributes = True


class ResultSchema(BaseModel):
    result_id: Optional[int] = Field(default=None) # Primary key; set by the database
    rank: int
    relevance_score: float
    case_id: int
    case_name: str
    case_date: date
    page_id: str
    page_number: int
    section_type: str
    concurring_voice: Optional[str] = Field(default=None)
    dissenting_voice: Optional[str] = Field(default=None)
    is_binding: Optional[bool] = Field(default=False)
    case_source: Optional[str] = Field(default=None)
    text_id: Optional[str] = Field(default=None) # Supposed to be chunk_id
    text: str
    # Relate to the query_id in the queryMetadata:
    query_id: Optional[int] = Field(default=None)

class ResponseSchema(BaseModel):
    results: List[ResultSchema] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

    def __str__(self) -> str:
        return "\n".join([str(result) for result in self.results])


class generatedSchema(BaseModel):
    query: str
    response: str
    citations: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
        extra = "forbid"

    def __str__(self) -> str:
        return super().__str__()