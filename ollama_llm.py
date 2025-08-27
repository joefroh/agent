from ollama import Client

class OllamaLLM:
    def __init__(self, model_string):
        self.model_name = model_string
        

    def __str__(self):
        return f"MyClass(param1={self.model_name})"
    
    def connect(self):
        self.client = Client(
        host='http://localhost:11434',
        headers={'x-some-header': 'some-value'}
        )
    
    def chat(self, message):
        response = self.client.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': message
            },
        ])

        print(response.message.content)