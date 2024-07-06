from fastapi import FastAPI

from ....workers.clip.encode import encode_image


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get_image_embeddings", tags=["encode"])
def get_image_embeddings(url: str):

    image, embeddings =  encode_image(url)

    return {"image": image, "embeddings": embeddings}
