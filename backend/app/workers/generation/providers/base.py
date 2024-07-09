from abc import ABC, abstractmethod

from typing import List

from ....schema.search import ResultSchema, generatedSchema


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, query: str, results: List[ResultSchema]) -> generatedSchema:
        pass