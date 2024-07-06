
from ...schema.search import ResponseSchema, ResultSchema, queryMetadata
from typing import List

from ...dependencies import supabase



def add_to_queries(query_metadata_: queryMetadata) -> int:
    try:
        res = supabase.from_("queries") \
                .insert({
                    # query_id will be generated automatically
                    "query": query_metadata_.query,
                    "api_key": query_metadata_.api_key,
                    "query_level": query_metadata_.query_level,
                    "index_id": query_metadata_.index_id,
                    "namespace_id": query_metadata_.namespace_id,
                    "archive_id": query_metadata_.archive_id,
                    "use_cache": query_metadata_.use_cache,
                    "max_results": query_metadata_.max_results,
                    }) \
                .execute()
        query_id = res.data[0]["query_id"]
        return query_id
    except Exception as e:
        print(f"Failed to add to queries: {str(e)}")
        return -1


def add_to_results(query_id_: int, query_results: ResponseSchema) -> bool:
    if query_results is None:
        print("No query results")
        return True
    for query_result in query_results:
        # Add the results to the database
        try:
            res = supabase.from_("results") \
                .insert({
                    # result_id will be generated automatically
                    "rank": query_result.rank,
                    "relevance_score": query_result.relevance_score,
                    "title": query_result.title,
                    "url": query_result.url,
                    "text_id": query_result.text_id,
                    "text": query_result.text,
                    "query_id": query_id_,
                    }) \
                .execute()

            # Check if results was added
            if len(res.data) <= 0:
                print("Failed to add to results")
                return False

        except Exception as e:
            print(f"Failed to add to results: {str(e)}")
            return False
    return True



def jsonify_results(query_results: List[ResultSchema]):
    results_ = []
    for _, result in enumerate(query_results):
        results_.append(
            {
                "rank": result.rank,
                "title": result.title,
                "URL": result.url,
                "text_id": result.text_id,
                "text": result.text,
                "relevance_score": result.relevance_score,
            }
            )
    json_response_ = {}
    json_response_["results"] = results_
    return json_response_