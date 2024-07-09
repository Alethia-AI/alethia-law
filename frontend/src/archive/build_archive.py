import requests

import os
BACKEND_URL="https://alethia-law.onrender.com"
backend_url = BACKEND_URL

# TODO: Upload cases to the backend, instead of sending links
def upload_case(name: str, case_path: str): 
    # Make a POST request to the backend with a timeout of 5 seconds
    try:
        print(backend_url)
        case_bytes = open(case_path, 'rb').read()
        response = requests.post(
                                backend_url + '/api/archives/cases/case/upload?api_key=' + name + '&file_name=' + case_path, 
                                files = {'pdf': case_bytes},
                                timeout=30
                                )
        if response.status_code != 200:
            print(response.status_code)
        else:
            return response.json()['message']
    except Exception as e:
        return f"Error: {e}"

    
def clear_archive():
    # Make a POST request to the backend with a timeout of 5 seconds
    response = requests.post(backend_url + '/clear-archive', timeout=5)
    if response.status_code != 200:
        print(response.status_code)

def get_archive():
    # Make a GET request to the backend with a timeout of 5 seconds
    response = requests.get(backend_url + '/get-archives', timeout=5)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        return None