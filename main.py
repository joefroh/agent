import ollama_llm
from utilities import print_messages

#model = ollama_llm.OllamaLLM('gemma3')
#model = ollama_llm.OllamaLLM('deepseek-r1')
#model = ollama_llm.OllamaLLM('llama3.1')
#model = ollama_llm.OllamaLLM('qwen2.5-coder:7b')
model = ollama_llm.OllamaLLM('qwen3')
model.connect()

while True:
    text = input(">")
    if text == "exit":
        break
    if text == "audit":
        print_messages(model.messages)
        continue
    model.user_chat(text)