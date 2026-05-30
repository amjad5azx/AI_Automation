from services.openrouter_service import ask_openrouter

def generate_response(prompt: str, provider: str = "openrouter"):
    if provider == "openrouter":
        return ask_openrouter(prompt)

    return {"error": "Invalid provider"}