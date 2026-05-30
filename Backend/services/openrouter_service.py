import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def ask_openrouter(prompt: str):
    if not OPENROUTER_API_KEY:
        return {"error": "API key not found in .env"}

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "poolside/laguna-xs.2:free",  # ← model string here
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    return response.json()