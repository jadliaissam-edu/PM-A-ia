"""
AgileFlow AI Service - FastAPI microservice
Powered by LangChain + OpenAI GPT-4o / Anthropic Claude API
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AgileFlow AI Service",
    description="AI-powered assistant for project management",
    version="1.0.0",
)

# CORS - allow Django backend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    project_id: str | None = None
    context: dict | None = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] | None = None


class TicketGenerationRequest(BaseModel):
    prompt: str
    project_id: str | None = None


class TicketGenerationResponse(BaseModel):
    title: str
    description: str
    priority: str | None = None
    labels: list[str] | None = None


# ── Health Check ────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "agileflow-ai"}


# ── Chatbot Endpoint ───────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    AI Chatbot endpoint - conversational assistant for project management.
    Uses LangChain with configured LLM provider.
    """
    try:
        # TODO: Implement LangChain chain with project context
        # llm = get_llm()
        # chain = get_chat_chain()
        # result = await chain.ainvoke({"message": request.message})
        return ChatResponse(
            reply="AI assistant is being configured. LangChain integration pending.",
            suggestions=[],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Ticket Generation Endpoint ─────────────────────────
@app.post("/generate-ticket", response_model=TicketGenerationResponse)
async def generate_ticket(request: TicketGenerationRequest):
    """
    Generate an issue/ticket description from a natural language prompt.
    """
    try:
        # TODO: Implement LangChain chain for ticket generation
        return TicketGenerationResponse(
            title="Generated Ticket",
            description=request.prompt,
            priority="Medium",
            labels=["ai-generated"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Description Suggestion Endpoint ────────────────────
@app.post("/suggest-description")
async def suggest_description(request: ChatRequest):
    """
    Suggest a description for an issue based on its title/context.
    """
    try:
        # TODO: Implement LangChain chain for description generation
        return {
            "description": "AI-generated description placeholder.",
            "confidence": 0.0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
