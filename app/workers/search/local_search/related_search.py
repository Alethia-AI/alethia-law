
from .archive_search import perform_archive_search
from ...embeddings.embeddings import prompt_embedding
from ..web_search.web_service import perform_search
from ....dependencies import supabase
from ..utils import get_prev_query_id

from ....schema.search import ResponseSchema


def perform_related_search(api_key: str, prompt: str, metric) -> ResponseSchema:
    top_result_title_ = None
    prev_query_id = get_prev_query_id(api_key)
    print(f"Previous query id: {prev_query_id}")
    if prev_query_id is None:
        embedding = prompt_embedding(prompt)
        query_results = perform_archive_search(api_key, embedding, metric)
        if query_results == [] or query_results is None:
            return query_results
        else:
            top_result_title_ = query_results[0]
    else:
        res = supabase.from_("results")\
            .select("title")\
            .eq("api_key", api_key)\
            .eq("query_id", prev_query_id)\
            .execute()
        print(f"Results: {res.data}")
        # Find all the titles from the result that equals the previous query_order.
        top_result_title_ = res.data[0]["title"]
    web_response: ResponseSchema = perform_search(api_key, top_result_title_)
    return web_response.results
