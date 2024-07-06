import json
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from ..workers.search.service import respond_to_search
from ..workers.search.utils import add_to_queries, add_to_results, jsonify_results
from ..workers.search.rerank import rerank

from ..schema.search import ResponseSchema, queryMetadata

router = APIRouter(
    prefix="/api",
    tags=['search'],
    dependencies=[],
)

@router.post('/search/')
async def search(query_metadata: queryMetadata, background_tasks: BackgroundTasks):
    prompt = query_metadata.query
    if not prompt:
        prompt = Request.args.get('query', '')
    if prompt:
        query_response: ResponseSchema = None
        try:
            print(query_metadata)
            query_response = respond_to_search(query_metadata)
            print(query_response)
            if query_response is None:
                return JSONResponse(content={"message": "Invalid query order."}, status_code=400)
        except Exception:
            return JSONResponse(content={"message": "There was an error while searching."}, status_code=400)

        # Re-rank the results
        query_response = await rerank(query_metadata, query_response)

        # Add the results to the database
        background_tasks.add_task(background_task, query_metadata, query_response.results)

        json_response_ = jsonify_results(query_response.results)

        return JSONResponse(content={"message": json_response_}, status_code=200)
    else:
        return 404

async def background_task(query_metadata_: queryMetadata, query_results: ResponseSchema):
    query_id: int =  add_to_queries(query_metadata_)
    if query_id == -1:
        print("Skipping adding to results")
        return
    add_to_results(query_id, query_results)
