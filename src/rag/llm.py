import os


def generate_answer(system_prompt, user_prompt, model=None):
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    if provider == "groq":
        return _generate_groq(system_prompt, user_prompt, model or "llama-3.1-8b-instant")
    return _generate_ollama(system_prompt, user_prompt, model or "llama3.2:3b")


def _generate_ollama(system_prompt, user_prompt, model):
    import ollama
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
    )
    return response["message"]["content"]


def _generate_groq(system_prompt, user_prompt, model):
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content