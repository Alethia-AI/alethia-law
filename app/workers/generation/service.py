import json
import os

from dotenv import load_dotenv
from fastapi import HTTPException

from ...schema.search import ResponseSchema, ResultSchema
from .providers.base import LLMProvider
from .providers.openai import OpenAILLMProvider
from .providers.anthropic import AnthropicLLMProvider

load_dotenv()



def get_openai_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI API key is not set in the environment variables. Please set the OPENAI_API_KEY environment variable or set GEN_PROVIDER to 'anthropic' or 'local'.",
        )
    return openai_api_key

def get_anthropic_api_key():
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="Tavily API key is not set in the environment variables. Please set the TAVILY_API_KEY environment variable or set SEARCH_PROVIDER to 'searxng' or 'serper'.",
        )
    return anthropic_api_key


def get_llm_provider() -> LLMProvider:
    llm_provider = os.getenv("LLM_PROVIDER")

    match llm_provider:
        case "openai":
            openai_api_key = get_openai_api_key()
            return OpenAILLMProvider(openai_api_key)
        case "serper":
            anthropic_api_key = get_anthropic_api_key()
            return AnthropicLLMProvider(anthropic_api_key)
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid search provider. Please set the SEARCH_PROVIDER environment variable to either 'searxng', 'tavily', 'serper', or 'bing'.",
            )


async def perform_generation(result: ResultSchema) -> ResponseSchema:
    llm_provider = get_llm_provider()

    try:
        generated_response = await llm_provider.generate(result.query, result)

        return generated_response
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while generating response."
        )
