from fastapi import FastAPI
from routers import agentic_rag, download_source

app = FastAPI(
    title="RAG API",
    description="API for RAG with Weaviate",
    version="1.0.0"
)

# Include routers
app.include_router(agentic_rag.router, prefix="/api/v1", tags=["rag"])
app.include_router(download_source.router, prefix="/api/v1", tags=["download", "source"])