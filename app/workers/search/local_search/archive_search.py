from ....schema.search import ResultSchema, ResponseSchema
from ...archives.docs import get_doc
from ....dependencies import supabase

from typing import List

def perform_archive_search(api_key, embedding, metric):
    # Search the archive
    matches = search_embeddings(api_key, embedding, metric)
    return ResponseSchema(results=archive_results(api_key, matches))

"""
Get matches from the vector database.
"""
def search_embeddings(api_key, embedding, metric, top_k=5, min_similarity_score=0.5):
    metric2function = {
        'cosine': 'cosine_similarity_search',
        'inner_product': 'inner_product_search',
    }
    print(f"Searching embeddings with metric {metric}")
    res = supabase.rpc(metric2function[metric], {
        'api_key': api_key,
        'embedding': embedding,
        'top_k': top_k,
        'min_similarity_score': min_similarity_score,
        }).execute()
    return [res.data]

"""
Given similar embeddings from the vector database, return the results.
"""
def archive_results(api_key, matches) -> list[ResultSchema]:
    results = []
    for i, match in enumerate(matches):
        doc = get_doc(api_key, match['doc_id'])
        if doc is None:
            print(f"Doc not found for {match['doc_id']}")
            return []
        result = ResultSchema(
            rank=i,
            relevance_score=match['similarity_score'],
            title=doc['title'],
            text_id=match['chunk_id'].split('-')[1], # FIXME: Should asign int id for chunk?
            text=match['text']
            )
        # See if match has url and add it to the result
        if 'url' in match:
            result.url = match['url']
        if 'doc_id' in match:
            result.text_id = match['doc_id']
        results.append(result)
    return results
