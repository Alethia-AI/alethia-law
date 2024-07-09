import json
import os

from dotenv import load_dotenv
from fastapi import HTTPException

from ....schema.search import ResponseSchema
from .providers.base import SearchProvider
from .providers.tavily import TavilySearchProvider

load_dotenv()



def get_tavily_api_key():
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise HTTPException(
            status_code=500,
            detail="Tavily API key is not set in the environment variables. Please set the TAVILY_API_KEY environment variable or set SEARCH_PROVIDER to 'searxng' or 'serper'.",
        )
    return tavily_api_key


def get_search_provider() -> SearchProvider:
    tavily_api_key = get_tavily_api_key()
    return TavilySearchProvider(tavily_api_key)


def perform_search(query: str) -> ResponseSchema:
    print("perform_search")
    search_provider = get_search_provider()

    try:
        web_response = search_provider.search(query)

        return web_response
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while searching."
        )
