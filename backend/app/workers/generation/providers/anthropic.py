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
            You are a legal research assistant tasked with answering queries based on retrieved case law information. Your goal is to provide accurate, well-cited answers to legal questions using the provided case information.

            Here is the query you need to answer:
            <query>
            {{QUERY}}
            </query>

            Below are the retrieved results from the case law database. Each result contains information about a relevant case, including its details and a relevant text excerpt:

            <results>
            {{RESULTS}}
            </results>

            Analyze the retrieved results carefully. Pay attention to the relevance scores, case details, and the text excerpts provided. Focus on the most relevant cases (those with higher relevance scores) and consider how they relate to the query.

            To answer the query:
            1. Identify the key legal principles and arguments presented in the relevant cases.
            2. Synthesize the information to form a comprehensive answer to the query.
            3. Ensure that every statement or proposition in your answer is supported by a citation to a specific case.
            4. If there are conflicting viewpoints in the cases, present both sides and explain the reasoning behind each.

            When citing cases, use the Bluebook citation format. For majority opinions, use the following format:
            Case Name, Volume U.S. Reports Page (Year)
            Example: New York Times Co. v. Tasini, 533 U.S. 483 (2001)

            For dissenting or concurring opinions, use this format:
            Case Name, Volume U.S. Reports Page, Specific Page (Year) (Justice's Last Name, J., dissenting/concurring)
            Example: Parker v. Randolph, 442 U.S. 62, 84 (1979) (Stevens, J., dissenting)

            Structure your answer as follows:
            1. Begin with a brief summary of the legal question and the key principles involved.
            2. Present the main argument or answer to the query, citing relevant cases.
            3. If applicable, discuss any conflicting viewpoints or dissenting opinions.
            4. Conclude with a concise restatement of the answer to the query.

            Ensure that every legal principle or argument is supported by an appropriate case citation.
            """

    async def generate(self, query_: str, results: List[ResultSchema]) -> generatedSchema:
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
                            "text": f"QUERY: {query_}, \n RESULTS: {results}."
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