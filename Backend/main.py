from fastapi import FastAPI
from pydantic import BaseModel
from services.llm_router import generate_response

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    provider: str = "openrouter"

@app.post("/chat")
def chat(request: ChatRequest):
    return generate_response(request.prompt, request.provider)