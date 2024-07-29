import openai


def get_openai_client():
    # Read OpenAI API key from file
    with open("OPENAI_ACCESS_TOKEN", "r") as file:
        api_key = file.read().strip()

    client = openai.OpenAI(api_key=api_key)
    return client


client = get_openai_client()


def ask_ai(user_prompt, system_prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return completion.choices[0].message.content
