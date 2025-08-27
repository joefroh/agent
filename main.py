import ollama_llm

model = ollama_llm.OllamaLLM('gemma3')
model.connect()

while True:
    text = input(">")
    model.chat(text)

print("end")