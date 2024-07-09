import requests
import re

import os


backend_url = os.getenv("BACKEND_URL")  # Get the backend URL from the environment variables

def generate_response(username: str, prompt: str):
    try:
        response = requests.post(
            backend_url + '/api/search/',
            data={
                "query": prompt,
                "api_key": username,
                "query_level": 0,
                "max_results": 5
            },
            timeout=50
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            # Log detailed error message
            error_details = response.json().get('error', 'Unknown error')
            print(f"Error {response.status_code}: {error_details}")
            return "Error in generating response."
    except Exception as e:
        print(e)
        return "Error in generating response."

def change_system_prompt(username, prompt):
    try:
        response = requests.post(
            backend_url + '/api/change-system-prompt',
            data={
                "api_key": username,
                "prompt": prompt
            },
            timeout=50
        )

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