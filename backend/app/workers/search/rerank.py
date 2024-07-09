import cohere
import os

from typing import List

from ...schema.search import ResponseSchema, ResultSchema, addQuery

co = cohere.AsyncClient(os.environ.get("COHERE_API_KEY"))

async def rerank(query: addQuery, responses: ResponseSchema) -> ResponseSchema:
    if responses is None:
        print("No results to rerank")
        return responses

    original_results_: List[ResultSchema] = responses.results

    documents_ = [result.model_dump() for result in original_results_]

    reranked_response = await co.rerank(
        model="rerank-english-v3.0",
        query= query.query,
        documents=documents_,
        rank_fields=["text", "title"],
        return_documents=False
        )

    reranked_results = []
    # Print the reranked response
    for i, result in enumerate(reranked_response.results):
        rank: int = result.index
        original_result: ResultSchema = original_results_[rank]
        original_result.relevance_score = result.relevance_score
        original_result.rank = i
        reranked_results.append(original_result)

    responses.results = reranked_results
    return responses
