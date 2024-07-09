# app.helpers.archive.py
import re
from typing import Union

from fastapi import HTTPException

from app.dependencies import supabase

from ...schema.archives.docs import Doc, Chunk
from ..embeddings.embeddings import build_embeddings

MIN_NUM_WORDS_PER_CHUNK = 20

# DOC HANDLERS:
def create_doc(doc: Doc, content: str):
    try:
        # Check if url already exists for the user
        # FIXME: Should update instead? What if the process fails after inserting url and title?
        if doc_exists("title", doc.title, doc.api_key):
            return False

        # Add user to users table
        res = supabase.from_("docs") \
            .insert({
                # doc_id will be generated automatically
                "api_key": doc.api_key,
                "title": doc.title,
                "tags": doc.tags
                }) \
            .execute()

        # Check if doc was added
        if len(res.data) <= 0:
            print("Failed to create doc")
            return False

        doc_id = res.data[0]["doc_id"]
        chunks = text2chunks(content)

        embeddings = build_embeddings(doc.title, chunks)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}-{i}"
            if chunk_exists("chunk_id", chunk_id):
                print("Chunk already exists")
                return False

            # Add only relevant embeddings
            if embeddings[i][0] == 1:
                res = supabase.from_("chunks") \
                    .insert({
                        "chunk_id": chunk_id,
                        "api_key": doc.api_key,
                        "doc_id": doc_id,
                        "text": chunk,
                        "embeddings": list(embeddings[i][1])
                        }) \
                    .execute()

                # Check if chunk was added
                if len(res.data) == 0:
                    # TODO: should I status code
                    print(f"Failed to create doc (Failed to insert {i+1} th chunk)")
                    return False

        return True

    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while archiving text."
        )

def text2chunks(text):
    chunks = []
    buffer = []
    num_words = 0
    num_paragraphs = 0

    for line in text.split("\n"):
        line = line.strip()
        if line != "":
            pattern = r'\[\d+\]'
            line = re.sub(pattern, '', line)
            buffer.append(line)
            num_words += len([w for w in line.split(" ") if w != ""])
        elif len(buffer) > 0:
            num_paragraphs += 1
            if num_words >= MIN_NUM_WORDS_PER_CHUNK:
                chunks.append(" ".join(buffer))
                buffer = []
                num_words = 0

    if len(buffer) > 0:
        chunks.append(" ".join(buffer))

    print(f"Number of paragraphs: {num_paragraphs}")
    print(f"Number of chunks: {len(chunks)}")
    return chunks

def doc_exists(key: str, value: str, api_key: str = None):
    if api_key is None:
        res = supabase.from_("docs").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by both api_key and key
        res = supabase.from_("docs").select("*") \
        .eq("api_key", api_key).eq(key, value) \
        .execute()
    return len(res.data) > 0

def chunk_exists(key: str, value: str, api_key: str = None):
    if api_key is None:
        res = supabase.from_("chunks").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by api_key and key
        res = supabase.from_("chunks").select("*") \
        .eq("api_key", api_key).eq(key, value) \
        .execute()
    return len(res.data) > 0

def get_doc(api_key: str, doc_id: int):
    print(f"Getting doc {doc_id}")
    res = get_docs(api_key, doc_id)
    return None if res is None else res[0]

def get_docs(api_key: str, doc_id: Union[int, None] = None):
    try:
        if doc_id is None:
            res = supabase.from_("docs") \
                .select("doc_id", "title", "tags") \
                .eq("api_key", api_key) \
                .execute()
            print(res.data)
            return res.data
        else:
            res = supabase.from_("docs") \
                .select("doc_id", "title", "tags") \
                .eq("api_key", api_key) \
                .eq("doc_id", doc_id) \
                .execute()
            print(res.data)
            return res.data
    except Exception as e:
        print(f"Error: {e}")
        return None

def delete_docs(api_key: str, doc_id: Union[int, None] = None):
    try:
        # Check if user exists
        success = False
        #if user_exists("api_key", api_key):
        if doc_id is None:
            # Delete all docs of the user
            # NOTE: Accosiated chukns will be deleted accordingly by casceding
            supabase.from_("docs")\
                .delete().eq("api_key", api_key) \
                .execute()
            success = True
        elif doc_exists(api_key, "doc_id", doc_id):
            # Delete the specified doc
            # NOTE: Accosiated chukns will be deleted accordingly by casceding
            supabase.from_("docs")\
                .delete().eq("api_key", api_key).eq("doc_id", doc_id) \
                .execute()
            success = True
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False

# CHUNK HANDLERS:
def get_chunk(api_key: int, chunk_id: str):
    res = get_chunks(api_key, chunk_id)
    return None if res is None else res[0]

def get_chunks(api_key: int, chunk_id: Union[str, None] = None):
    try:
        if chunk_id is None:
            res = supabase.from_("chunks") \
                .select("*") \
                .eq("api_key", api_key) \
                .execute()
            print(res.data)
            return res.data
        else:
            res = supabase.from_("chunks")\
                .select("*") \
                .eq("api_key", api_key).eq("chunk_id", chunk_id) \
                .execute()
            print(res.data)
            return res.data
    except Exception as e:
        print(f"Error: {e}")
        return None
