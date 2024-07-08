
from ...schema.search import ResponseSchema, ResultSchema, addQuery
from typing import List

from ...dependencies import supabase



def add_to_queries(query: addQuery) -> int:
    try:
        print("Adding to queries")
        res = supabase.from_("queries") \
                .insert({
                    # query_id will be generated automatically
                    "query": query.query,
                    "api_key": query.api_key,
                    "query_level": query.query_level,
                    "max_results": query.max_results,
                    }) \
                .execute()
        query_id = res.data[0]["query_id"]
        print(f"Added to queries with query_id: {query_id}")
        return query_id
    except Exception as e:
        print(f"Failed to add to queries: {str(e)}")
        return -1


def add_to_results(query_id_: int, query_results: ResponseSchema) -> bool:
    if query_results is None:
        print("No query results")
        return True
    print("Adding to results for query_id: ", query_id_)
    for query_result in query_results:
        # Add the results to the database
        try:
            res = supabase.from_("results") \
                .insert({
                    # result_id will be generated automatically
                    "rank": query_result.rank,
                    "relevance_score": query_result.relevance_score,
                    "case_id": query_result.case_id,
                    "case_name": query_result.case_name,
                    "case_date": query_result.case_date,
                    "page_id": query_result.page_id,
                    "page_number": query_result.page_number,
                    "section_type": query_result.section_type,
                    "concurring_voice": query_result.concurring_voice,
                    "dissenting_voice": query_result.dissenting_voice,
                    "is_binding": query_result.is_binding,
                    "case_source": query_result.case_source,
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
    print("Added to results")
    return True



def jsonify_results(query_results: List[ResultSchema]):
    results_ = []
    for _, result in enumerate(query_results):
        results_.append(
            {
                "rank": result.rank,
                "relevance_score": result.relevance_score,
                "case_id": result.case_id,
                "case_name": result.case_name,
                "case_date": result.case_date,
                "page_id": result.page_id,
                "page_number": result.page_number,
                "section_type": result.section_type,
                "concurring_voice": result.concurring_voice,
                "dissenting_voice": result.dissenting_voice,
                "is_binding": result.is_binding,
                "case_source": result.case_source,
                "text_id": result.text_id,
                "text": result.text,
                "query_id": result.query_id,
            }
            )
    json_response_ = {}
    json_response_["results"] = results_
    return json_response_