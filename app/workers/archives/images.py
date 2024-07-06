
from app.dependencies import supabase
from ..users.users import user_exists
from ...schema.archive.docs import Image, Pixel


# IMAGE HANDLERS:
def create_image(image: Image):
    try:
        # Check if url already exists for the user
        # FIXME: Should update instead? What if the process fails after inserting url and title?
        if image_exists("url", image.url, image.api_key):
            print(f"URL already exists: {image.url}")
            return False

        # Add user to users table
        res = supabase.from_("images") \
            .insert({
                # url_id will be generated automatically
                "api_key": image.api_key,
                "url": image.url,
                }) \
            .execute()

        # Check if doc was added
        if len(res.data) <= 0:
            print("Failed to create image")
            return False

        image_id = res.data[0]["image_id"]

        embeddings = image.embeddings

        for i, embedding in enumerate(embeddings):
            pixel_id = f"{image_id}-{i}"
            if pixel_exists("pixel_id", pixel_id):
                print("Pixel already exists")
                return False

            # Add only relevant embeddings
            res = supabase.from_("pixels") \
                .insert({
                    "pixel_id": pixel_id,
                    "api_key": image.api_key,
                    "image_id": image_id,
                    "embedding": embedding
                    }) \
                .execute()

            # Check if pixel was added
            if len(res.data) == 0:
                # TODO: should I status code
                print(f"Failed to create image (Failed to insert {i+1} th embedding)")
                return False

        return True

    except Exception as e:
        print(f"Failed to create image: {str(e)}")
        return False

def image_exists(key: str, value: str, api_key: str = None):
    if api_key is None:
        res = supabase.from_("images").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by both api_key and key
        res = supabase.from_("images").select("*") \
        .eq("api_key", api_key).eq(key, value) \
        .execute()
    return len(res.data) > 0

def pixel_exists(key: str, value: str, api_key: str = None):
    if api_key is None:
        res = supabase.from_("pixels").select("*") \
        .eq(key, value) \
        .execute()
    else:
        # Filter by api_key and key
        res = supabase.from_("pixels").select("*") \
        .eq("api_key", api_key).eq(key, value) \
        .execute()
    return len(res.data) > 0
