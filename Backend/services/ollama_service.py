import requests

def ask_ollama(prompt):
    return requests.post(
        "http://host.docker.internal:11434/api/generate",
        json={
            "model": "llama3.2-vision",
            "prompt": prompt,
            "stream": False
        }
    ).json()