import requests


class Archive:

    def __init__(self, username: str, backend_url: str):
        self.username = username
        self.backend_url = backend_url
        
    def upload_case(self, case_path: str): 
        # Make a POST request to the backend with a timeout of 5 seconds
        try:
            print(self.backend_url)
            case_bytes = open(case_path, 'rb').read()
            response = requests.post(
                                    self.backend_url + '/api/archives/cases/case/upload?api_key=' + self.username + '&file_name=' + case_path, 
                                    files = {'pdf': case_bytes},
                                    timeout=30
                                    )
            if response.status_code != 200:
                print(response.status_code)
            else:
                return response.json()['message']
        except Exception as e:
            return f"Error: {e}"

        
    def clear_archive(self):
        # Make a POST request to the backend with a timeout of 5 seconds
        response = requests.post(self.backend_url + '/clear-archive', timeout=5)
        if response.status_code != 200:
            print(response.status_code)

    def get_archive(self):
        # Make a GET request to the backend with a timeout of 5 seconds
        response = requests.get(self.backend_url + '/get-archives', timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            return None