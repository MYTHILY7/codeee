import openai
from config import OPENAI_API_KEY, MODEL_NAME

openai.api_key = OPENAI_API_KEY

def summarize_text(text):
    text = text[:3000]  # optional: prevent too-long inputs
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert summarizer. Summarize text in 3–4 lines, clearly and concisely."},
                {"role": "user", "content": f"{text}"}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        return f"[Summary failed: {e}]"