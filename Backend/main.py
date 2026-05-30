"""
AI DevOps Chat API — FastAPI
Endpoint: POST /chat
Response shape matches React frontend:
  data?.choices?.[0]?.message?.content
"""

import os
import re
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ── Load env vars FIRST (correction from review doc) ──────────────────────────
load_dotenv()

app = FastAPI(
    title="AI DevOps Chat API",
    description="Multi-provider AI chat endpoint via OpenRouter",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Constants ──────────────────────────────────────────────────────────────────
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

PROVIDER_MODELS = {
    "openrouter": "poolside/laguna-xs.2:free",
    "claude":     "anthropic/claude-sonnet-4-5",
    "gpt4":       "openai/gpt-4o",
    "gemini":     "google/gemini-2.5-pro",
}


# ── Request Schema ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    prompt: str
    provider: str = "openrouter"


# ── Leaked tag cleaner ─────────────────────────────────────────────────────────
def strip_leaked_tags(text: str) -> str:
    """Remove leaked system/role tags that some models emit."""
    return re.sub(r"<\/?(assistant|system|user|human)>", "", text).strip()


# ── Core logic ─────────────────────────────────────────────────────────────────
async def generate_response(prompt: str, provider: str) -> dict:
    """
    Calls OpenRouter and returns the raw choices[] shape so the React frontend
    can read:  data?.choices?.[0]?.message?.content
    Leaked tags are stripped from the content before returning.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY is not configured. Set it in your .env file.",
        )

    model = PROVIDER_MODELS.get(provider, PROVIDER_MODELS["openrouter"])

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",       # correct format
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8001",     # recommended
                    "X-Title": "AI DevOps Chat API",            # recommended
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"OpenRouter error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")

    data = response.json()

    # Strip leaked tags from every choice's content
    for choice in data.get("choices", []):
        content = choice.get("message", {}).get("content", "")
        choice["message"]["content"] = strip_leaked_tags(content)

    return data   # ← returns { choices: [...], model, ... } — matches React frontend


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Body:     { "prompt": "...", "provider": "openrouter" | "claude" | "gpt4" | "gemini" }
    Response: { "choices": [{ "message": { "content": "..." } }], ... }
    """
    return await generate_response(request.prompt, request.provider)


@app.get("/test-openrouter")
async def test_openrouter():
    """Verifies API key is loaded without exposing it."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return {
        "has_key": bool(api_key),
        "key_length": len(api_key) if api_key else 0,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/providers")
async def list_providers():
    return {"providers": list(PROVIDER_MODELS.keys()), "models": PROVIDER_MODELS}


# ── Dev server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
