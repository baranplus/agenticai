# Agentic RAG System

This project implements an Agentic RAG (Retrieval-Augmented Generation) system using FastAPI and Weaviate. The system features a sophisticated agent-based architecture for improved query processing and response generation.

## Features

- Agent-based RAG architecture
- Question rewriting for improved retrieval
- Document grading for relevance assessment
- Persian (Farsi) language support
- Docker containerization
- Basic authentication for vector stores

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Make sure port 8700 (API) is available
- Weaviate should be accessible at port 8500 on the configured host

## Project Structure

```
.
├── app/
│   ├── agents/          # Agent-based RAG components
│   ├── db/             # Database and vector store implementations
│   ├── llm/            # LLM configurations and templates
│   ├── routers/        # FastAPI routes
│   ├── schema/         # Data models
│   └── utils/          # Utility functions
├── docker-compose.yaml
├── Dockerfile.Base
└── requirements.txt
```

## Environment Setup

1. Create a `.env` file in the project root with the following structure:

```env
# Docker Services
APP_IMAGE=agentic_rag:1.0.0
APP_PORT=8700

# LLM Configuration
API_KEY=your_api_key
BASE_URL=your_base_url
GENERATION_MODEL=your_model_name
EMBEDDING_MODEL=your_embedding_model

# Weaviate Configuration
WEAVIATE_HOST=weaviate
WEAVIATE_PORT=port
WEAVIATE_USER_KEY=root_user_key
HYBRID_SEARCH_ALPHA= 1.0 pure vector search, 0.0 pure keyword search
```

## Installation and Running

1. First, build the Docker images:
```bash
# Build the FastAPI application image
docker build -t agentic_rag:1.0.0 -f Dockerfile.Base .
```

2. Start the services using Docker Compose:
```bash
# Start all services
docker-compose up -d

# To see the logs
docker-compose logs -f

# To stop all services
docker-compose down
```

3. The services will be available at:
   - FastAPI application: http://host:8700
   - Weaviate: http://host:8500

## API Usage

The main RAG endpoint is available at:
```
POST /api/v1/query

{
    "message": "Your question",
    "collection": "your_collection_name",
    "top_k": 3,
    "use_local_embedding": true
}
```

Example using curl:
```bash
curl -X POST "http://localhost:8700/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "What are the rules?",
           "collection": "my_collection",
           "top_k": 3,
           "use_local_embedding": false
         }'
```

## Development

To run the project locally for development:

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI application:
```bash
uvicorn app.main:app --reload --port 8000
```

## Troubleshooting

1. If you get authentication errors:
   - Check if the `.env` file contains the correct credentials
   - Verify the authentication settings in both ChromaDB and Weaviate services

2. If the services don't start:
   - Check if the required ports are available
   - Verify Docker and Docker Compose installation
   - Check the logs using `docker-compose logs`

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details