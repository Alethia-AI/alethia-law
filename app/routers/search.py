import json
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from ..workers.search.service import respond_to_search
from ..workers.search.utils import add_to_queries, add_to_results, jsonify_results
from ..workers.search.rerank import rerank

from ..schema.search import ResponseSchema, addQuery

router = APIRouter(
    prefix="/api",
    tags=['search'],
    dependencies=[],
)

@router.post('/search/')
async def search(query_: addQuery, background_tasks: BackgroundTasks):
    prompt = query_.query
    if not prompt:
        prompt = Request.args.get('query', '')
    if prompt:
        query_response: ResponseSchema = None
        try:
            print(query_)
            query_response = respond_to_search(query_)
            print(query_response)
            if query_response is None:
                return JSONResponse(content={"message": "Invalid query order."}, status_code=400)
        except Exception:
            return JSONResponse(content={"message": "There was an error while searching."}, status_code=400)

        # Re-rank the results
        query_response = await rerank(query_, query_response)

        # Add the results to the database
        background_tasks.add_task(background_task, query_, query_response.results)

        json_response_ = jsonify_results(query_response.results)

        return JSONResponse(content={"message": json_response_}, status_code=200)
    else:
        return 404

async def background_task(query_: addQuery, query_results: ResponseSchema):
    query_id: int =  add_to_queries(query_)
    if query_id == -1:
        print("Skipping adding to results")
        return
    add_to_results(query_id, query_results)
