import anthropic
import os
import re
import time

from typing import List

from fastapi import HTTPException

from .base import LLMProvider
from ....schema.search import ResultSchema, generatedSchema


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.SYSTEM_PROMPT = """
            You will be provided with context(s) delimited by triple quotes
            and a unique id for each context with format [unique_id], where unique_id is a tuple of two numbers,
            along with a prompt. 

            Your task is to answer the question using only the provided passages and to cite the passage(s)
            used to answer the question with their unique ids.

            If there is no Context, then simply write: "Information insufficient in archive."
        """

    async def generate(self, query_: str, results: List[ResultSchema]) -> generatedSchema:
        context = ""
        for i, result in enumerate(results):
            context += f'"{result.case_name}"\n{result.text}\n\n'
        output = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.5,
            system=self.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Context: {context}\nQuestion: {query_}"
                        }
                    ]
                }
            ]
        )
        response = output.content[0].text
        processed_response = await self.post_process(query_, response, results)
        print(processed_response)
        return processed_response
    
    async def post_process(self, query_: str, response: str, results: ResultSchema) -> generatedSchema:
        try:    #response = re.sub(r'\[\(\d+, \d+\)\]', '', response)
            generatedResponse = generatedSchema(query=query_, response=response, results=results)
            return generatedResponse
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="There was an error while post-processing the response.",
            )