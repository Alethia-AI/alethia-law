from ....schema.search import ResultSchema, ResponseSchema, addQuery
from ...archives.cases import get_page, get_case

from ....dependencies import supabase

from typing import List

def perform_archive_search(query: addQuery, embedding, metric):
    #print(embedding)
    # Search the archive
    matches = search_embeddings(query.api_key, embedding, metric, top_k=query.max_results)
    return ResponseSchema(results=archive_results(query.api_key, matches))

"""
Get matches from the vector database.
"""
def search_embeddings(api_key, embedding, metric, top_k=5, min_similarity_score=-2.0):
    metric2function = {
        'cosine': 'cosine_similarity_search',
        'inner_product': 'inner_product_search',
    }
    print(f"Searching embeddings with metric {metric}")
    try:
        res = supabase.rpc(metric2function[metric], {
            #'api_key': api_key,
            'query_embedding': embedding,
            'match_count': top_k,
            'match_threshold': min_similarity_score,
            }).execute()
        print(f"Got response: {res}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print(f"Got {len(res.data)} matches")
    return res.data

"""
Given similar embeddings from the vector database, return the results.
"""
def archive_results(api_key, matches) -> list[ResultSchema]:
    results = []
    for i, match in enumerate(matches):
        print(f"Match {i} with score {match['similarity_score']}")
        page = get_page(api_key, match['page_id'])
        case = get_case(api_key, page['case_id'])
        if page is None:
            print(f"Page not found for {match['page_id']}")
            return []
        print(f"Matched page {page['page_number']} from case {case['case_name']}")
        result = ResultSchema(
            rank=i,
            relevance_score=match['similarity_score'],
            case_id=case['case_id'],
            case_name=case['case_name'],
            case_date=case['case_date'],
            page_id=page['page_id'],
            page_number=page['page_number'],
            section_type=page['section_type'],
            concurring_voice=page['concurring_voice'],
            dissenting_voice=page['dissenting_voice'],
            is_binding=page['is_binding'],
            case_source=case['case_source'],
            text_id=match['chunk_id'],
            text=match['text'],
        )
        print(f"Result: {result}")
        results.append(result)
    return results
