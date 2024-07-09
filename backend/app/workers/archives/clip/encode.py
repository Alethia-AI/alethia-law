from PIL import Image
import requests

from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def encode_image(url: str):
    image = Image.open(requests.get(url, stream=True).raw)

    # FIXME: This does not produce the required embeddings
    embeddings = model.encode_image(processor(images=image, return_tensors="pt").pixel_values)

    return image, embeddings
