from supabase import create_client, Client

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

def create_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_API_KEY")
    supabase: Client = create_client(url, key)

    # Check if connection was successful
    if supabase is None:
        raise Exception("Failed to connect to Supabase")
    
    # Check if the schema exists
    schema = "public"
    if not supabase.schema(schema):
        raise Exception(f"Schema '{schema}' does not exist in the database")

    return supabase
