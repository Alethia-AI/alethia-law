import requests

class ResponseGenerator:

    def __init__(self, username: str, backend_url: str):
        self.username = username
        self.backend_url = backend_url

    def generate_response(self, prompt: str):
        try:
            response = requests.post(
                self.backend_url + '/api/search/' +
                f"?api_key={self.username}&query={prompt}&query_level=1&max_results=5",
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

    def change_system_prompt(self, prompt: str):
        try:
            print(f"Changing system prompt to: {prompt}")
            print(f"Backend URL: {self.backend_url}")
            response = requests.post(
                self.backend_url + '/api/change-system-prompt/'+
                f"?api_key={self.username}&prompt={prompt}",
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
        
    def get_system_prompt(self):
        try:
            response = requests.get(
                self.backend_url + '/api/get-system-prompt/' +
                f"?api_key={self.username}",
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
    
    def non_augmented_generator(self, prompt: str):
        try:
            response = requests.post(
                self.backend_url + '/api/n-search/' +
                f"?api_key={self.username}&query={prompt}&query_level=1&max_results=5",
                timeout=50
            )

            if response.status_code == 200:
                return response.json()['response']
            else:
                # Log detailed error message
                error_details = response.json().get('error', 'Unknown error')
                print(f"Error {response.status_code}: {error_details}")
                return "Error in generating response.", []
        except Exception as e:
            print(e)
            return "Error in generating response.", []