from enum import unique
from fastapi import APIRouter, requests
from fastapi.responses import JSONResponse

import os
import time
from datetime import datetime
import httpx


from ....schema.archives.images import Image, imageMetadata
from ....workers.archives.images import create_image, get_images, delete_images

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


@router.post("/image/add")
async def add_image_to_archives(imageMetadata_: imageMetadata):
    """
    Adds images to the archive.
    @param imageMetadata_: metadata of the image to be added.
    @return: JSONResponse
    """
    try:
        image = Image(
            api_key=imageMetadata_.api_key,
            image=imageMetadata_.image,
            title=imageMetadata_.title,
            caption=imageMetadata_.caption,
            tags=imageMetadata_.tags
        )
        res = create_image(image)
        if not res:
            return JSONResponse(content={"message": "Failed to archive image"}, status_code=400)
    except Exception as e:
            error_message = f"An error occurred while downloading the file: {str(e)}"
            print(error_message)
            return JSONResponse({'error': error_message}), 500
    return JSONResponse(content={"message": f"{imageMetadata_.id} archived successfully"}, status_code=200)


@router.get("/images/get")
async def get_images_from_archives(api_key: str):
    """
    Retrieves images from the archive.
    @param api_key: api_key of the user.
    @return: JSONResponse
    """
    try:
        res = get_images(api_key)
        if not res:
            return JSONResponse(content={"message": "Failed to retrieve images"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": "error in processing images; " + str(e)}, status_code=400)
    
    return JSONResponse(content=res, status_code=200)


@router.delete("/images/delete")
async def delete_images_from_archives(api_key: str):
    """
    Deletes images from the archive.
    @param api_key: api_key of the user.
    @return: JSONResponse
    """
    try:
        res = delete_images(api_key)
        if not res:
            return JSONResponse(content={"message": "Failed to delete images"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": "error in processing images; " + str(e)}, status_code=400)
    
    return JSONResponse(content={"message": "Images deleted successfully"}, status_code=200)