from fastapi import FastAPI
from routers import agentic_rag

app = FastAPI(
    title="RAG API",
    description="API for RAG with Weaviate",
    version="1.0.0"
)

# Include routers
app.include_router(agentic_rag.router, prefix="/api/v1", tags=["rag"])