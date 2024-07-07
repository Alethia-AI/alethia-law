# app.helpers.archive.py
import re
from typing import Union, List

from fastapi import HTTPException

from app.dependencies import supabase

from ...schema.archives.cases import Case, Page, CreatePage
from ..embeddings.embeddings import build_embeddings


# DOC HANDLERS:
def create_case(case: Case, pages: List[CreatePage]):
    try:
        for page in pages:
            print(page.__dict__)
        print("Creating case")
        # Check if case_name already exists for the user
        if case_exists("case_name", case.case_name, case.api_key):
            raise HTTPException(
                status_code=400, detail="Case already exists"
            )
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
            .execute()
        print("Case added to supabase")

        # Check if case was added
        if len(res.data) <= 0:
            raise HTTPException(
                status_code=500, detail="Failed to create case"
            )

        case_id = res.data[0]["case_id"]
        print(f"Case ID: {case_id}")

        embeddings = build_embeddings(case.case_name, pages)

        print("Embeddings built")

        for i, page in enumerate(pages):
            page_id = f"{case_id}-{i}"
            if page_exists("page_id", page_id):
                print("Page already exists")
                raise HTTPException(
                    status_code=400, detail="Page already exists"
                )

            # Add only relevant embeddings
            if embeddings[i][0] == 1:
                res = supabase.from_("pages") \
                    .insert({
                        "page_id": page_id,
                        "api_key": case.api_key,
                        "case_id": case_id,
                        "text": page.text,
                        "section_type": page.section_type,
                        "page_number": page.page_number,
                        "is_binding": page.is_binding,
                        "concurring_voice": page.concurring_voice,
                        "dissenting_voice": page.dissenting_voice,
                        "embeddings": list(embeddings[i][1])
                        }) \
                    .execute()

                # Check if page was added
                if len(res.data) == 0:
                    # TODO: should I status code
                    print(f"Failed to create case (Failed to insert {i+1} th page)")
                    return False
        print("Case created successfully")  

        return True

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="There was an error while archiving text: " + str(e)
        )

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
    return len(res.data) > 0

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
