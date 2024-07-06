from fastapi import HTTPException

import os
import redis
import json

from typing import List

from ..embeddings.embeddings import prompt_embedding
from .local_search.archive_search import perform_archive_search
from .web_search.web_service import perform_search
#from .related_search import perform_related_search

from app.schema.search import ResultSchema, ResponseSchema, queryMetadata


METRIC = "inner_product"
#METRIC = "cosine"

#redis_url = os.getenv("REDIS_URL")
#redis_client = redis.Redis.from_url(redis_url) if redis_url else None

def respond_to_search(queryMetadata_: queryMetadata) -> ResponseSchema:
    # TODO: Add support for the following:
            # - max_results.
            # - archive_id, namespace_id, index_id.
            # - use_cache.
    try:
        #cache_key = f"search:{queryMetadata.prompt}"
        #if redis_client and (cached_results := redis_client.get(cache_key)):
        #    cached_json = json.loads(json.loads(cached_results.decode("utf-8")))  # type: ignore
        #    return ResponseSchema(**cached_json)
        try:
            query_response: ResponseSchema = None
            if queryMetadata_.query_level == 0:
                web_response: ResponseSchema = perform_search(queryMetadata_.query)
                query_response = web_response
            elif queryMetadata_.query_level == 1:
                embedding = prompt_embedding(queryMetadata_.query)
                query_response = perform_archive_search(queryMetadata_.api_key, embedding, metric=METRIC)
            else:
                raise HTTPException(
                        status_code=500, detail="Invalid query order: 0 is for web search and 1 is for local archive search."
                    )
        except Exception:
            raise HTTPException(
                    status_code=500, detail="There was an error while searching."
                )

        #if redis_client:
        #    redis_client.set(cache_key, json.dumps(query_response.model_dump_json()), ex=7200)

        return query_response
    except Exception:
        raise HTTPException(
                    status_code=500, detail="There was an error while searching."
                )
