import json
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from ..workers.search.service import respond_to_search
from ..workers.search.utils import add_to_queries, add_to_results, jsonify_results
from ..workers.search.rerank import rerank
from ..workers.generation.service import perform_generation, jsonify_generated_response, change_system_prompt, get_system_prompt

from ..schema.search import ResponseSchema, addQuery

router = APIRouter(
    prefix="/api",
    tags=['search'],
    dependencies=[],
)

@router.post('/search/')
async def search(api_key: str, query: str, query_level: str, max_results: str, background_tasks: BackgroundTasks):
    try:
        query_ = addQuery(
            query=query,
            api_key=api_key,
            query_level=int(query_level),
            max_results=int(max_results)
            )
        print(query_)
        prompt = query_.query
        if not prompt:
            prompt = Request.args.get('query', '')
        if prompt:
            query_response: ResponseSchema = None
            try:
                query_response = respond_to_search(query_)
                print(query_response)
                if query_response is None:
                    return JSONResponse(content={"message": "Invalid query order."}, status_code=400)
            except Exception as e:
                return JSONResponse(content={"message": "There was an error while searching: " + str(e)}, status_code=400)

            # Re-rank the results
            query_response = await rerank(query_, query_response)

            # Add the results to the database
            background_tasks.add_task(background_task, query_, query_response.results)

            #json_response = jsonify_results(query_response.results)

            response = await perform_generation(query_, query_response.results)

            return JSONResponse(content={"response": response.response}, status_code=200)
        else:
            return 404
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "There was an error while searching: " + str(e)}, status_code=400)

@router.get('/get-system-prompt/')
async def get_prompt(api_key: str):
    try:
        response = get_system_prompt(api_key)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "There was an error while getting the system prompt: " + str(e)}, status_code=400)


@router.post('/change-system-prompt/')
async def change_prompt(api_key: str, prompt: str):
    try:
        response = change_system_prompt(api_key, prompt)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "There was an error while changing the system prompt: " + str(e)}, status_code=400)

async def background_task(query_: addQuery, query_results: ResponseSchema):
    query_id: int =  add_to_queries(query_)
    if query_id == -1:
        print("Skipping adding to results")
        return
    add_to_results(query_id, query_results)
