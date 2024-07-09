import anthropic
import os
import re
import time
import json

from typing import List

from fastapi import HTTPException

from .base import LLMProvider
from ....schema.search import ResultSchema, generatedSchema


STARTING_PROMPT = """
            You are a legal research assistant tasked with answering queries based on retrieved case law information. 
            Your goal is to provide accurate, well-cited answers to legal questions using the provided case information.

            You will be provided with a message history and the current query along with a list of retrieved results related to the current query formatted as follows:
            ... 
            (Previous messages)
            ...
            Query: [Current_Query]
            Results:
            [Citation]
            Text: [Text Excerpt]
            [Citation]
            Text: [Text Excerpt]
            ...
            Analyze the retrieved results carefully. Pay attention to the text excerpts provided.
            Please ensure that _every_ legal principle or argument is supported by an appropriate citation to the case law from Results above.
            """


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.SYSTEM_PROMPT = STARTING_PROMPT

    async def generate(self, query_list_dict: list[dict], results_: List[ResultSchema]) -> generatedSchema:
        print("Generating response from Anthropic...")
        print(query_list_dict)
        try:
            user_query, current_query, text_results_ = self.pre_process(query_list_dict, results_)
            print("---------------------------")
            print(user_query)
            print("---------------------------")
            output = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.5,
            system=self.SYSTEM_PROMPT,
            messages=user_query,
            )
            response = output.content[0].text
            processed_response = self.post_process(current_query, response, results_, text_results_)
            #print(processed_response)
            return processed_response
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="There was an error while generating the response." + str(e),
            )
    
    def pre_process(self, query_list_dict: list[dict], results_: List[ResultSchema]) -> str:
        current_query = query_list_dict[-1]["content"]
        #print(current_query)
        # For #1 proper Bluebook citation format, here’s an example: New York Times Co. v. Tasini, 533 U.S. 483 (2001)
        concurr = lambda case: f" ({case.concurring_voice}, concurring)" if case.concurring_voice else f""
        dissent = lambda case: f" ({case.dissenting_voice}, dissenting)" if case.dissenting_voice else f""
        bluebook_format = lambda case: f"{case.case_name}, {case.case_source} ({case.case_date.year}){concurr(case)}{dissent(case)}" if case.case_source else f"{case.case_name} ({case.case_date.year})"
        citations = [bluebook_format(result) for result in results_]
        results = [f"**[{citations[i]}]**\n\n *Text:* {result.text}" for i, result in enumerate(results_)]
        current_query_results = """Query: {query}\nResults:\n{results}""".format(query=current_query, results=results)
        current_query_dict = {"role": "user", "content": current_query_results}
        #print(current_query_dict)
        query_list_dict[-1] = current_query_dict
        return query_list_dict, current_query, results
    
    def post_process(self, query_: str, response: str, results_, citations: List[str]) -> generatedSchema:
        try:
            print("Post-processing response...")
            print(response)
            case_names = [result.case_name for result in results_]
            # Italicize case names
            for case_name in case_names:
                response = response.replace(f"{case_name}", f"*{case_name}*")
            print(response)
            return generatedSchema(query=query_, response=response, citations=citations)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500,
                detail="There was an error while post-processing the response.",
            )
    
    def get_system_prompt(self) -> str:
        try:
            return self.SYSTEM_PROMPT
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="There was an error while getting the system prompt.",
            )
        
    def change_system_prompt(self, prompt: str) -> bool:
        try:
            self.SYSTEM_PROMPT = prompt
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="There was an error while changing the system prompt.",
            )
            return False