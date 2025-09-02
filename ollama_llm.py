from ollama import Client
from ollama import _types
from utilities import create_message
import tools


class OllamaLLM:
    system_prompt = create_message(
        "system",
        "/no_think You are a helpful assistant who keeps things brief and responds only in english. Not every prompt requires a tool, if you don't think you need to use one - just respond normally as if you didn't have any provided. When in doubt, do the simplest thing, and keep responses concise.",
    )
    initial_user_prompt = create_message("user", "hello")

    default_options = {"temperature": 0.1, "stop": ["<think></think>"]}
    default_tools = [
        tools.list_files,
        tools.get_now,
        tools.get_forecast,
        tools.get_location,
    ]

    def __init__(self, model_string):
        self.model_name = model_string
        self.messages = [self.system_prompt, self.initial_user_prompt]

        self.client = None
        self.tools = self.default_tools
        self.support_tools = True  # Assume Tools are supported by default, if they aren't handle it gracefully later

    def __str__(self):
        return f"MyClass(param1={self.model_name})"

    def push_message(self, role, message, tool_name=None):
        self.messages.append(create_message(role, message, tool_name))

    def connect(self):
        self.client = Client(host="http://localhost:11434")  # talk to local ollama
        response = self.client.chat(model=self.model_name, messages=self.messages)
        self.push_message("assistant", response.message.content)
        print(response.message.content)

    def user_chat(self, message):
        self.push_message("user", message)
        response = self.__send_messages_to_llm()

        self.__handle_response(response)

    def handle_tools(self, tool_calls):
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            args = tool_call.function.arguments

            for tool in self.tools:
                if tool_name == tool.__name__:
                    print(f"DEBUG: Calling tool {tool_name}.")
                    result = tool(**args)
                    self.push_message("tool", result.__str__(), tool_name)

    def __handle_response(self, response):
        if response.message.tool_calls:
            self.handle_tools(response.message.tool_calls)
            response = self.__send_messages_to_llm()
            self.__handle_response(response)
        else:
            self.push_message("assistant", response.message.content)
            print(response.message.content)

    def __send_messages_to_llm(self, options=default_options):
        if self.support_tools:
            try:
                return self.client.chat(
                    model=self.model_name,
                    messages=self.messages,
                    options=options,
                    tools=self.tools,
                )
            except _types.ResponseError as e:
                if e.error.__contains__("does not support tools"):
                    self.support_tools = (
                        False  # Set tool support to false and fall through
                    )
                else:  # Got some other type of error we haven't handled yet - spit it out and kill the process
                    print(e.error)
                    exit(-1)

        return self.client.chat(
            model=self.model_name, messages=self.messages, options=options
        )
