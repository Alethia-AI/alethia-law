from enum import unique
from fastapi import APIRouter, requests
from fastapi.responses import JSONResponse

import os
import time
from datetime import datetime
import httpx

from ...schema.archives.cases import Case
from ...workers.archives.cases import create_case, get_cases, delete_cases, create_pages
from ...workers.archives.processing.cases import process_legal_document
from ...workers.archives.processing.pdf2text import processor
#from ..schema.archive.images import Image, imageMetadata
#from ..workers.archive.images import create_image, get_images, delete_images

router = APIRouter(
    prefix="/api/archives/cases",
    tags=['case'],
    dependencies=[],
)

LOG_FILE = 'request_log.txt'


def log_request(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'{timestamp} - {message}\n'
    with open(LOG_FILE, 'a') as file:
        file.write(log_entry)

class TimeRecorder:
    def __init__(self, process="", is_print=True):
        self.process_ = process
        self.is_print_ = is_print
        self.start_t_ = time.time()
        self.prev_t_ = self.start_t_
        self.record_ = {"sub": [], "total": None}

    def lap(self, subprocess):
        s = time.time()
        d = s - self.prev_t_
        if self.is_print_:
            print(f"[Time] {subprocess} in {self.process_}: {d}")
        self.record_["sub"].append({subprocess: d})
        self.prev_t_ = s

    def stop(self):
        s = time.time()
        d = s - self.start_t_
        if self.is_print_:
            print(f"[Time] {self.process_}: {d}")
        self.record_["total"] = d
        self.prev_t_ = s

    def get_record(self):
        return self.record_

@router.post("/case/add")
async def add_case_to_archives(api_key: str, pdf_path: str):
    """
    Adds cases to the archive.
    @param archiveMetadata_: metadata of the case to be added.
    @return: JSONResponse
    """
    try:
        print(f"Converting pdf to text at {pdf_path}")
        # Check if the file exists
        text_path = pdf_path.replace(".pdf", ".txt")
        if not os.path.exists(text_path):
            text_path = await processor.process_file(pdf_path)
        print(f"Processing case at {text_path}")
        pages, case_name, case_date, case_source = process_legal_document(text_path)
        print(f"Case name: {case_name}")
        if pages is [] or case_name is None:
            return JSONResponse(content={"message": "case content is missing"}, status_code=400)
        # Make case_date a datetime object
        case_date = datetime.strptime(case_date, "%m/%d/%Y")
        case = Case(
            api_key=api_key,
            case_name=case_name,
            case_date=case_date,
            case_source=case_source
            )
        
        case_id = create_case(case)

        if not case_id:
            return JSONResponse(content={"message": f"Failed to archive case + {case_id}"}, status_code=400)

        res = create_pages(case_id, case, pages)
        
        if not res:
            return JSONResponse(content={"message": f"Failed to archive page + {res}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": "error in processing case; " + str(e)}, status_code=400)
    return JSONResponse(content={"message": f"{case.case_name} archived successfully"}, status_code=200)

@router.post("/case/add_dir")
async def add_directory_to_archives(api_key: str, dir_path: str):
    """
    Adds all the cases in a directory to the archive.
    @param api_key: API key of the user.
    @param dir_path: Path of the directory containing the cases.
    @return: JSONResponse
    """
    try:
        # First convert the pdf to text
        print(f"Converting pdf to text at {dir_path}")
        # Check if the file exists
        files = os.listdir(dir_path)
        for file in files:
            pdf_path = os.path.join(dir_path, file)
            print(f"Converting pdf to text at {pdf_path}")
            # Check if the file exists
            text_path = pdf_path.replace(".pdf", ".txt")
            if not os.path.exists(text_path):
                text_path = await processor.process_file(pdf_path)
            print(f"Processing case at {text_path}")
            pages, case_name, case_date, case_source = process_legal_document(text_path)
            print(f"Case name: {case_name}")
            if pages is [] or case_name is None:
                return JSONResponse(content={"message": "case content is missing"}, status_code=400)
            # Make case_date a datetime object
            case_date = datetime.strptime(case_date, "%m/%d/%Y")
            case = Case(
                api_key=api_key,
                case_name=case_name,
                case_date=case_date,
                case_source=case_source
                )
            
            case_id = create_case(case)

            if not case_id:
                return JSONResponse(content={"message": f"Failed to archive case + {case_id}"}, status_code=400)

            res = create_pages(case_id, case, pages)
            
            if not res:
                return JSONResponse(content={"message": f"Failed to archive page + {res}"}, status_code=400)
            
    except Exception as e:
        return JSONResponse(content={"message": "error in processing case; " + str(e)}, status_code=400)
    return JSONResponse(content={"message": f"{dir_path} archived successfully"}, status_code=200)

@router.get("/case/get")
async def get_cases_from_archives(api_key: str):
    """
    Get all the archives of the user.
    @param api_key: API key of the user.
    @return: JSONResponse
    """
    # Get all cases of the user
    cases = get_cases(api_key=api_key, case_id=None)
    if cases is not None:
        return JSONResponse(content={"message": "Cases found", "cases": cases}, status_code=200)
    else:
        return JSONResponse(content={"message": "Cases not found"}, status_code=200)


@router.delete("/case/delete")
async def clear_cases(api_key: str):
    """
    Delete all the cases of the user.
    @param api_key: API key of the user.
    @return: JSONResponse
    """
    # Delete all cases of the user
    if delete_cases(api_key=api_key, case_id=None):
        return JSONResponse(content={"message": "Cases deleted successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Cases deletion failed"}, status_code=400)