import openai

API_KEY = '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'

openai.api_key = API_KEY

prompt = f"Ecris moi une conclusion d'un article qui parle de l'utilisation de l'API ChatGPT"

completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [{
        "role": "user",
        "content": prompt
    }]
)

print(completion['choices'][0]['message']['content'])