import ollama_llm

model = ollama_llm.OllamaLLM('gemma3')
model.connect()

while True:
    text = input(">")
    if text == "exit":
        break
    if text == "audit":
        print(model.messages)
        continue
    model.chat(text)