from ollama import Client
from utilities import create_message
import tools

class OllamaLLM:
    system_prompt = create_message('system',"You are a helpful assistant who keeps things brief and responds only in english. If you must use a tool for no reason use 'do_nothing' but don't say anything about it.")
    initial_user_prompt = create_message('user','hello')

    def __init__(self, model_string):
        self.model_name = model_string
        self.messages = [
            self.system_prompt, self.initial_user_prompt
        ]
        self.tools = [
            tools.list_files,
            tools.do_nothing
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
        response = self.client.chat(model=self.model_name, messages=self.messages, tools=self.tools)
        if response.message.tool_calls and response.message.tool_calls[0].function.name != "do_nothing":
            self.handle_tools(response.message.tool_calls)
            return
        if response.message.tool_calls and response.message.tool_calls[0].function.name == "do_nothing":
            response = self.client.chat(model=self.model_name, messages=self.messages)
        
        self.push_message('assistant', response.message.content)
        print(response.message.content)

    def handle_tools(self, tool_calls):
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments

            for tool in self.tools:
                if tool_name == tool.__name__:
                    result = tool(**args)
                    self.push_message('tool', result.__str__())
                    response = self.client.chat(model=self.model_name, messages=self.messages, tools=self.tools)
                    self.push_message('assistant', response.message.content)
                    print(response.message.content)