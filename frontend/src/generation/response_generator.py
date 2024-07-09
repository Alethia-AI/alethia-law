import requests
import re


#BACKEND_URL="https://alethia-law.onrender.com"
BACKEND_URL="http://localhost:5001"
backend_url = BACKEND_URL

def generate_response(username: str, prompt: str):
    try:
        response = requests.post(
            backend_url + '/api/search/' +
            f"?api_key={username}&query={prompt}&query_level=1&max_results=5",
            timeout=50
        )

        if response.status_code == 200:
            return response.json()['response'], response.json()['results']
        else:
            # Log detailed error message
            error_details = response.json().get('error', 'Unknown error')
            print(f"Error {response.status_code}: {error_details}")
            return "Error in generating response.", []
    except Exception as e:
        print(e)
        return "Error in generating response.", []

def change_system_prompt(username: str, prompt: str):
    try:
        print(f"Changing system prompt to: {prompt}")
        print(f"Backend URL: {backend_url}")
        response = requests.post(
            backend_url + '/api/change-system-prompt/'+
            f"?api_key={username}&prompt={prompt}",
            timeout=50
        )

        print(response.json())
        if response.status_code == 200:
            return response.json()['response']
        else:
            # Log detailed error message
            error_details = response.json().get('error', 'Unknown error')
            print(f"Error {response.status_code}: {error_details}")
            return {}
    except Exception as e:
        print(e)
        return {}
    
def get_system_prompt(username: str):
    try:
        response = requests.get(
            backend_url + '/api/get-system-prompt/' +
            f"?api_key={username}",
            timeout=50
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            # Log detailed error message
            error_details = response.json().get('error', 'Unknown error')
            print(f"Error {response.status_code}: {error_details}")
            return "Error in getting system prompt."
    except Exception as e:
        print(e)
        return "Error in getting system prompt."