import ollama_llm

model = ollama_llm.OllamaLLM('gemma3')
model.connect()

while True:
    text = input(">")
    if text == "exit":
        break
    model.chat(text)