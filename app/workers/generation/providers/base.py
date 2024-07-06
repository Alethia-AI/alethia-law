from abc import ABC, abstractmethod

from ....schema.search import ResponseSchema


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, query: str) -> ResponseSchema:
        pass