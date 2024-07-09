import json
import os

from typing import List

from dotenv import load_dotenv
from fastapi import HTTPException

from ...schema.search import generatedSchema, ResultSchema, addQuery
from .providers.base import LLMProvider
from .providers.openai import OpenAILLMProvider
from .providers.anthropic import AnthropicLLMProvider

load_dotenv()



def get_openai_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI API key is not set in the environment variables. Please set the OPENAI_API_KEY environment variable or set LLM_PROVIDER to 'anthropic' or 'local'.",
        )
    return openai_api_key

def get_anthropic_api_key():
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="Anthropic API key is not set in the environment variables. Please set the ANTHROPIC_API_KEY environment variable or set LLM_PROVIDER to 'openai'.",
        )
    return anthropic_api_key


def get_llm_provider() -> LLMProvider:
    llm_provider = os.getenv("LLM_PROVIDER")

    match llm_provider:
        case "openai":
            openai_api_key = get_openai_api_key()
            return OpenAILLMProvider(openai_api_key)
        case "anthropic":
            anthropic_api_key = get_anthropic_api_key()
            return AnthropicLLMProvider(anthropic_api_key)
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid llm provider. Please set the LLM_PROVIDER environment variable to either 'anthropic' or 'openai'.",
            )

def change_system_prompt(api_key: str, prompt: str) -> str:
    llm_provider = get_llm_provider()

    try:
        response = llm_provider.change_system_prompt(prompt)
        return response
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while changing the system prompt."
        )

def get_system_prompt(api_key: str) -> str:
    llm_provider = get_llm_provider()

    try:
        response = llm_provider.get_system_prompt()
        return response
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while getting the system prompt."
        )

async def perform_generation(query_: addQuery, results: List[ResultSchema]) -> generatedSchema:
    llm_provider = get_llm_provider()

    try:
        print("Generating response...")
        generated_response = await llm_provider.generate(query_.query, results)

        return generated_response
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while generating response."
        )

async def jsonify_generated_response(generated_response: generatedSchema) -> str:
    return json.dumps(generated_response.dict(), indent=4)