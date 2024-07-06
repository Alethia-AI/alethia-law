from typing_extensions import Unpack
from pydantic import BaseModel, ConfigDict
from pydantic.fields import Field
from typing import List, Optional

class queryMetadata(BaseModel):
    query_id: Optional[int] = Field(default=None)
    query: str
    api_key: str
    query_level: int # 0 for web search, 1 for image search
    index_id: Optional[str] = Field(default=None)
    namespace_id: Optional[str] = Field(default=None)
    archive_id: Optional[str] = Field(default=None)
    use_cache: Optional[bool] = Field(default=True)
    max_results: int = 3

    class Config:
        from_attributes = True


class ResultSchema(BaseModel):
    result_id: Optional[int] = Field(default=None) # Primary key; set by the database
    rank: int
    relevance_score: float
    title: str
    url: Optional[str] = Field(default=None)
    text_id: Optional[str] = Field(default=None)
    text: str
    # Relate to the query_id in the queryMetadata:
    query_id: Optional[int] = Field(default=None)

class ResponseSchema(BaseModel):
    results: List[ResultSchema] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

    def __str__(self) -> str:
        return "\n".join([str(result) for result in self.results])
