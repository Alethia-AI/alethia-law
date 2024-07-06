import anthropic
import os
import re
import time

from .base import LLMProvider
from ....schema.search import ResponseSchema, ResultSchema


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
            
            If an answer to the question is provided, it must be annotated with a unique id. 
            Format the citations using the following format "[unique id]".

            Example: The sky is blue [(1, 2)]. The grass is green [(2, 3)].
            A citation instance CANNOT contain more than one unique id!
        """

    async def generate(self, prompt: str, results: ResultSchema) -> ResponseSchema:
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
                            "text": f"Context: {results}\nQuestion: {prompt}"
                        }
                    ]
                }
            ]
        )
        response = output.content[0].text
        return self.post_process(response, results)
    
    async def post_process(self, response: str, results: ResultSchema) -> ResponseSchema:
        # TODO:: Implement post processing.
        response = re.sub(r'\[\(\d+, \d+\)\]', '', response)
        return response