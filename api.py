from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.router import Router

app = FastAPI(
    title="LLM Router",
    description="Auto-routes prompts to the right model tier based on complexity. Tracks cost and latency.",
    version="1.0.0",
)

_router = Router()


class CompletionRequest(BaseModel):
    prompt: str
    complexity: Optional[str] = None  # simple | medium | complex
    max_tokens: int = 1024
    system: str = ""
    provider: str = "anthropic"


@app.post("/complete")
def complete(req: CompletionRequest):
    if req.complexity and req.complexity not in ("simple", "medium", "complex"):
        raise HTTPException(400, "complexity must be simple, medium, or complex")
    r = Router(provider=req.provider)
    return r.complete(req.prompt, req.complexity, req.max_tokens, req.system)


@app.get("/stats")
def stats():
    return _router.stats()


@app.get("/health")
def health():
    return {"status": "ok"}
