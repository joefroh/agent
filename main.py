import ollama_llm

#model = ollama_llm.OllamaLLM('gemma3')
#model = ollama_llm.OllamaLLM('deepseek-r1')
model = ollama_llm.OllamaLLM('llama3.1')
model.connect()

while True:
    text = input(">")
    if text == "exit":
        break
    if text == "audit":
        print(model.messages)
        continue
    model.chat(text)
