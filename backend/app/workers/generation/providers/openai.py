from openai import OpenAI
import os
import re
import time

from .base import LLMProvider
from ....schema.search import ResponseSchema, ResultSchema


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def prompt_model(self, prompt, context):
        SYSTEM_PROMPT = """
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
        citations = ""
        for uid_pid, content in context.items():
            #print(uid_pid)
            citations += f'"\"\"\"{content}\"\"\" [{uid_pid[0], uid_pid[1]}]"\n'
        user_prompt = f"Context: {citations}\nQuestion: {prompt}"
        #print(user_prompt)
        prompt_for_model =[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        return prompt_for_model

    async def generate(self, prompt: str, results: ResultSchema) -> ResponseSchema:
        output = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.prompt_model(prompt, results.context),
            stream=False
        )
        response = output.choices[0].message.content
        return response
    
    # TODO:: Implement post processing.
    async def post_process(self, response: str, results: ResultSchema) -> ResponseSchema:
        response = re.sub(r'\[\(\d+, \d+\)\]', '', response)
        return response