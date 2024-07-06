from enum import unique
from fastapi import APIRouter, requests
from fastapi.responses import JSONResponse

import os
import time
from datetime import datetime
import httpx

from ...schema.archives.docs import Doc, textMetadata
from ...workers.archives.docs import create_doc, get_docs, delete_docs
#from ..schema.archive.images import Image, imageMetadata
#from ..workers.archive.images import create_image, get_images, delete_images

router = APIRouter(
    prefix="/api/archives",
    tags=['text'],
    dependencies=[],
)

LOG_FILE = 'request_log.txt'

WEBPROCESS_BACKEND = os.getenv('WEBPROCESS_BACKEND')
IMAGE_BACKEND = os.getenv('IMAGE_BACKEND')

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

@router.post("/text/add")
async def add_text_to_archives(textMetadata_: textMetadata):
    """
    Adds documents to the archive.
    @param archiveMetadata_: metadata of the document to be added.
    @return: JSONResponse
    """
    try:
        try:
            content = textMetadata_.content
            if content is None:
                return JSONResponse(content={"message": "text content is missing"}, status_code=400)
            title = textMetadata_.title
            tags = textMetadata_.tags
            doc = Doc(
                api_key=textMetadata_.api_key,
                title=textMetadata_.title,
                tags=textMetadata_.tags
            )
            res = create_doc(doc, content)
            if not res:
                return JSONResponse(content={"message": "Failed to archive text"}, status_code=400)
        except Exception as e:
            return JSONResponse(content={"message": "error in processing text; " + str(e)}, status_code=400)
    except Exception as e:
        return {"message": str(e)}, 400
    return JSONResponse(content={"message": f"{doc.title} archived successfully"}, status_code=200)


@router.get("/text/get")
async def get_text_from_archives(api_key: str):
    """
    Get all the archives of the user.
    @param api_key: API key of the user.
    @return: JSONResponse
    """
    # Get all docs of the user
    docs = get_docs(api_key=api_key, doc_id=None)
    if docs is not None:
        return JSONResponse(content={"message": "Archives found", "archives": docs}, status_code=200)
    else:
        return JSONResponse(content={"message": "Archives not found"}, status_code=200)


@router.delete("/text/delete")
async def clear_archives(api_key: str):
    """
    Delete all the archives of the user.
    @param api_key: API key of the user.
    @return: JSONResponse
    """
    # Delete all docs of the user
    if delete_docs(api_key=api_key, doc_id=None):
        return JSONResponse(content={"message": "Archives deleted successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Archives deletion failed"}, status_code=400)