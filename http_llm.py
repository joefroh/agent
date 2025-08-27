import requests
import json

class http_llm:
    def __init__(self, model_string):
        self.model_name = model_string

    def __str__(self):
        return f"MyClass(param1={self.model_name})"
    
    def connect(self):
        # Ollama API endpoint (default)
        url = "http://localhost:11434/api/generate"

        # Define the request payload
        data = {
            "model": self.model_name,  # Replace with your downloaded model name
            "prompt": "Whats my name",
            "stream": False # Set to True for streaming responses
        }

        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # Raise an exception for bad status codes
            result = response.json()
            print(result['response'])
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")