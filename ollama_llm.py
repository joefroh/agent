from ollama import Client
from utilities import create_message

class OllamaLLM:
    system_prompt = create_message('system','You are a helpful assistant who keeps things brief.')
    initial_user_prompt = create_message('user','hello')

    def __init__(self, model_string):
        self.model_name = model_string
        self.messages = [
            self.system_prompt, self.initial_user_prompt
        ]
        self.client = None

    def __str__(self):
        return f"MyClass(param1={self.model_name})"

    def push_message(self, role, message):
        self.messages.append(create_message(role,message))

    def connect(self):
        self.client = Client(
            host='http://localhost:11434',  # talk to local ollama
            headers={'x-some-header': 'some-value'}
        )
        response = self.client.chat(model=self.model_name, messages=self.messages)
        self.push_message('assistant', response.message.content)
        print(response.message.content)

    def chat(self, message):
        self.push_message('user', message)
        response = self.client.chat(model=self.model_name, messages=self.messages)
        self.push_message('assistant', response.message.content)
        print(response.message.content)
