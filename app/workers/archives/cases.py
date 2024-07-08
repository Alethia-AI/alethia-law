# app.helpers.archive.py
import re
from typing import Union, List

from fastapi import HTTPException

from app.dependencies import supabase

from ...schema.archives.cases import Case, Page, CreatePage
from ..embeddings.embeddings import build_embeddings

MIN_NUM_WORDS_PER_CHUNK = 20
MAX_NUM_WORDS_PER_CHUNK = 100

# DOC HANDLERS:
def create_case(case: Case):
    try:
        print("Creating case")
        # Check if case_name already exists for the user
        if case_exists("case_name", case.case_name, case.api_key) is not None:
            print("Case already exists")
            return case_exists("case_name", case.case_name, case.api_key)
        
        print("Case does not exist")

        # Add user to users table
        res = supabase.from_("cases") \
            .insert({
            # case_id will be generated automatically
            "api_key": case.api_key,
            "case_name": case.case_name,
            "case_date": case.case_date.strftime("%Y-%m-%d"),
            "case_source": case.case_source
            }) \
            .execute(       )  
        print("Case added to supabase")

        # Check if case was added
        if len(res.data) <= 0:
            raise HTTPException(
                status_code=500, detail="Failed to create case"
            )

        case_id = res.data[0]["case_id"]
        print(f"Case ID: {case_id}")

        print("Case created successfully")  

        return case_id

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="There was an error while archiving case: " + str(e)
        )

def create_pages(case_id: int, case: Case, pages: List[Page]):
    try:
        for i, page in enumerate(pages):
            page_id = f"{case_id}-{i}"
            if page_exists("page_id", page_id):
                print("Page already exists for page_id", page_id)
                continue
            
            print(f"Creating page {page_id}")
            # Add only relevant embeddings
            res = supabase.from_("pages") \
                .insert({
                    "page_id": page_id,
                    "api_key": case.api_key,
                    "case_id": case_id,
                    "section_type": page.section_type,
                    "page_number": page.page_number,
                    "is_binding": page.is_binding,
                    "concurring_voice": page.concurring_voice,
                    "dissenting_voice": page.dissenting_voice
                    }) \
                .execute()

            # Check if page was added
            if len(res.data) == 0:
                # TODO: should I status code
                print(f"Failed to create case (Failed to insert {i+1} th page)")
                raise HTTPException(
                    status_code=500, detail="Failed to create case (Failed to insert {i+1} th page)"
                )
            
            print(f"Page {page_id} created successfully")

            chunks = page2chunks(page.text)
            embeddings = build_embeddings(case.case_name, chunks)

            for j, chunk in enumerate(chunks):
                chunk_id = f"{page_id}-{j}"
                if chunk_exists("chunk_id", chunk_id):
                    print("Chunk already exists")
                    continue
                print(f"Creating chunk {chunk_id}")

                # Add only relevant embeddings
                if embeddings[j][0] == 1:
                    res = supabase.from_("chunks") \
                        .insert({
                            "chunk_id": chunk_id,
                            "api_key": case.api_key,
                            "page_id": page_id,
                            "text": chunk,
                            "embeddings": list(embeddings[j][1])
                            }) \
                        .execute()

                    # Check if chunk was added
                    if len(res.data) == 0:

                        print(f"Failed to create case (Failed to insert {j+1} th chunk)")
                        raise HTTPException(
                            status_code=500, detail="Failed to create case (Failed to insert {j+1} th chunk)"
                        )
                print(f"Chunk {chunk_id} created successfully")
        
        return case_id
    except Exception as e:
        raise HTTPException(
        status_code=500, detail="There was an error while archiving page : " + str(e)
    )

def page2chunks(text):
    #print(text)
    chunks = []
    buffer = []
    num_words = 0
    num_paragraphs = 0
    lines = text.split("\n")

    print(f"Number of lines: {len(lines)}")

    for i, line in enumerate(lines):
        line = line.strip()

        # Remove redundant spaces
        line = re.sub(' +', ' ', line)
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
        if num_words >= MAX_NUM_WORDS_PER_CHUNK:
            chunks.append(" ".join(buffer))
            buffer = []
            num_words = 0
            num_paragraphs += 1

    if len(buffer) > 0:
        chunks.append(" ".join(buffer))

    print(f"Number of paragraphs: {num_paragraphs}")
    print(f"Number of chunks: {len(chunks)}")
    return chunks

def case_exists(key: str, value: str, api_key: str = None):
    print(f"Checking if case exists with {key}={value}")
    if api_key is None:
        res = supabase.from_("cases").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by both api_key and key
        res = supabase.from_("cases").select("*") \
        .eq("api_key", api_key).eq(key, value) \
        .execute()
    if len(res.data) > 0:
        # return case_id
        case_id = res.data[0]["case_id"]
        print(f"Case exists with {key}={value} and case_id={case_id}")
        return case_id        
    else:
        return None

def page_exists(key: str, value: str, api_key: str = None):
    if api_key is None:
        res = supabase.from_("pages").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by api_key and key
        res = supabase.from_("pages").select("*") \
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

def get_case(api_key: str, case_id: int):
    print(f"Getting case {case_id}")
    res = get_cases(api_key, case_id)
    return None if res is None else res[0]

def get_cases(api_key: str, case_id: Union[int, None] = None):
    try:
        if case_id is None:
            res = supabase.from_("cases") \
                .select("case_id", "case_name", "case_date", "case_source") \
                .eq("api_key", api_key) \
                .execute()
            print(res.data)
            return res.data
        else:
            res = supabase.from_("cases") \
                .select("case_id", "case_name", "case_date", "case_source") \
                .eq("api_key", api_key) \
                .eq("case_id", case_id) \
                .execute()
            print(res.data)
            return res.data
    except Exception as e:
        print(f"Error: {e}")
        return None

def delete_cases(api_key: str, case_id: Union[int, None] = None):
    try:
        # Check if user exists
        success = False
        #if user_exists("api_key", api_key):
        if case_id is None:
            # Delete all cases of the user
            # NOTE: Accosiated chukns will be deleted accordingly by casceding
            supabase.from_("cases")\
                .delete().eq("api_key", api_key) \
                .execute()
            success = True
        elif case_exists(api_key, "case_id", case_id):
            # Delete the specified case
            # NOTE: Accosiated chukns will be deleted accordingly by casceding
            supabase.from_("cases")\
                .delete().eq("api_key", api_key).eq("case_id", case_id) \
                .execute()
            success = True
        return success
    except Exception as e:
        print(f"Error: {e}")
        return False

# CHUNK HANDLERS:
def get_page(api_key: int, page_id: str):
    res = get_pages(api_key, page_id)
    return None if res is None else res[0]

def get_pages(api_key: int, page_id: Union[str, None] = None):
    try:
        if page_id is None:
            res = supabase.from_("pages") \
                .select("*") \
                .eq("api_key", api_key) \
                .execute()
            print(res.data)
            return res.data
        else:
            res = supabase.from_("pages")\
                .select("*") \
                .eq("api_key", api_key).eq("page_id", page_id) \
                .execute()
            print(res.data)
            return res.data
    except Exception as e:
        print(f"Error: {e}")
        return None
