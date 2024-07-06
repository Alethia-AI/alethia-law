from abc import ABC, abstractmethod

from .....schema.search import ResponseSchema


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, api_key, query: str) -> ResponseSchema:
        pass
