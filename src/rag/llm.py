import ollama


def generate_answer(system_prompt, user_prompt, model="llama3.2:3b"):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0},
    )
    return response["message"]["content"]