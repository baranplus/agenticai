# Agentic RAG System

This project implements an Agentic RAG (Retrieval-Augmented Generation) system using FastAPI, LangGraph workflows, and Weaviate. The system features a sophisticated workflow-based architecture with specialized nodes for improved query processing and response generation.

## Features

- **Workflow-based RAG Architecture** with specialized processing nodes:
  - Question rewriting and keyword extraction for improved retrieval
  - Document retrieval and relevance assessment from vector stores
  - Source attribution with downloadable document references
  - Natural language to SQL query conversion
  - Decision points for intelligent routing between RAG and SQL modes
  - Answer generation with source citations
- **Multi-language Support**: Optimized for Persian (Farsi) and other languages with proper text handling
- **Integrated Data Source Support**:
  - **Weaviate**: Vector search for document retrieval with hybrid search capabilities
  - **MongoDB**: Source document storage with metadata support
  - **SQL Server**: Structured data querying with schema caching for performance
  - **Downloadable Sources**: UTF-8 encoded file support for Persian/Arabic filenames
- **Production-Ready Deployment**:
  - Docker containerization with Docker Compose orchestration
  - Authentication for all data stores
  - SQL schema caching for optimized query performance
  - Configurable workflow parameters via YAML files
- **Interactive Weaviate UI**: Streamlit-based interface for:
  - Visual exploration of document collections
  - Advanced hybrid search capabilities
  - Source-based filtering and statistics
  - Document content and metadata viewing

## Prerequisites

### For Local Development
- Python 3.12+
- pip/poetry for dependency management
- Access to external services (LLM API, Weaviate, MongoDB, SQL Server)

### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+
- Ports 8700, 8501 available (configurable via `.env`)
- Network connectivity to external services (Weaviate, MongoDB, SQL Server)

## Project Structure

```
.
├── app/
│   ├── ai/                     # AI/LLM integrations
│   │   ├── embedding.py        # Embedding model configurations
│   │   ├── llm.py             # LLM provider setup
│   │   └── prompts.py         # System prompts and templates
│   ├── db/                     # Database clients
│   │   ├── mongodb_client.py   # MongoDB integration for source documents
│   │   ├── sql_client.py       # SQL Server integration for structured data
│   │   ├── weaviate_client.py  # Weaviate vector store integration
│   │   └── __init__.py
│   ├── workflows/              # LangGraph workflow definitions
│   │   ├── graph.py           # Main workflow graph orchestration
│   │   ├── states.py          # Workflow state definitions
│   │   ├── configs/           # Workflow configuration loaders
│   │   │   ├── agentic_rag.py      # RAG workflow config
│   │   │   ├── smart_sql.py        # SQL workflow config
│   │   │   ├── load_config.py      # Config file loader utility
│   │   │   └── __init__.py
│   │   ├── nodes/             # Workflow processing nodes
│   │   │   ├── extract_keywords.py    # Extract search keywords from queries
│   │   │   ├── retriever.py           # Document retrieval from Weaviate
│   │   │   ├── generate_answer.py     # LLM-based answer generation
│   │   │   ├── sourcing.py           # Source attribution and link generation
│   │   │   ├── sql.py                # SQL query generation and execution
│   │   │   ├── decision_point.py     # RAG vs SQL routing logic
│   │   │   ├── filename_detection.py # Source document identification
│   │   │   ├── merge.py              # Result merging and deduplication
│   │   │   ├── return_docs.py        # Document collection return logic
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── routers/                # FastAPI route handlers
│   │   ├── agentic_rag.py     # Main /api/v1/query endpoint
│   │   ├── download_source.py # /api/v1/download endpoint
│   │   ├── smart_sql.py       # /api/v1/sql/query endpoint (optional)
│   │   └── __init__.py
│   ├── schema/                 # Request/response data models
│   │   ├── request.py         # Input validation schemas
│   │   ├── response.py        # Output response schemas
│   │   └── __init__.py
│   ├── configs/                # Application configuration
│   │   ├── env_configs.py     # Environment variable loading
│   │   └── __init__.py
│   ├── utils/                  # Utility functions
│   │   ├── logger.py          # Logging setup
│   │   └── __init__.py
│   ├── main.py                # FastAPI application entry point
│   └── __init__.py
├── assets/                     # Runtime configuration and cache files
│   ├── agentic_rag_config_custom.yaml     # Custom RAG workflow config
│   ├── agentic_rag_config.yaml            # Default RAG workflow config
│   ├── smart_sql_config.yaml              # SQL workflow configuration
│   ├── prompts.yaml                       # LLM prompts and templates
│   └── schema_cache.json                  # Cached SQL database schema
├── weaviate_ui/                # Streamlit UI for Weaviate exploration
│   ├── app.py                 # Streamlit application
│   ├── Dockerfile             # UI container definition
│   ├── requirements.txt        # UI dependencies
│   └── README.md
├── docker-compose.yaml         # Docker Compose service orchestration
├── Dockerfile.Base             # Base Docker image definition
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Environment Setup

### 1. Create `.env` File

Create a `.env` file in the project root with the following configuration:

```env
# ============================================================================
# Docker Service Configuration
# ============================================================================
APP_IMAGE=agentic_rag:1.0.0
WEAVIATE_UI_IMAGE=weaviate_ui:1.0.0
APP_PORT=8700
WEAVIATE_UI_PORT=8501

# ============================================================================
# LLM Provider Configuration
# ============================================================================
# Choose one LLM provider configuration below

## Option 1: OpenRouter (Recommended)
API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BASE_URL=https://openrouter.ai/api/v1
GENERATION_MODEL=openai/gpt-4o
SQL_GENERATION_MODEL=openai/gpt-4-turbo

## Option 2: AvalAI (Alternative)
# API_KEY=aa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# BASE_URL=https://api.avalai.ir/v1
# GENERATION_MODEL=gpt-4o
# SQL_GENERATION_MODEL=gpt-4-turbo

# ============================================================================
# Embedding Model Configuration
# ============================================================================
# Use external embedding service or local embeddings
EMBEDDING_URL=http://embedding-service-host:port/v1/embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ============================================================================
# Weaviate Configuration
# ============================================================================
WEAVIATE_HOST=weaviate-host-ip-or-domain
WEAVIATE_PORT=8100
WEAVIATE_GRPC_PORT=50052
WEAVIATE_USER_KEY=your-weaviate-user-key
HYBRID_SEARCH_ALPHA=0.25  # 0.0=pure keyword, 0.5=balanced, 1.0=pure vector

# ============================================================================
# MongoDB Configuration
# ============================================================================
MONGODB_URI=mongodb://mongodb-host:port
MONGODB_INITDB_DEV_USERNAME=root
MONGODB_INITDB_DEV_PASSWORD=your-mongodb-password

# ============================================================================
# SQL Server Configuration
# ============================================================================
SQL_HOST=sql-server-host-ip
SQL_PORT=9002
SQL_USER=sql-user
SQL_PASS=your-sql-password-with-special-chars-url-encoded
SQL_DB=target-database-name
SQL_METADATA_CACHE_PATH=/app/assets/schema_cache.json
SQL_REQUIRED_TABLES=table1,table2,table3  # Comma-separated list of tables to include
SQL_ENDPOINT_ENABLED=false  # Set to true to enable /api/v1/sql/query endpoint

# ============================================================================
# Workflow Configuration
# ============================================================================
AGENTIC_RAG_WORKFLOW_CONFIG_PATH=/app/assets/agentic_rag_config_custom.yaml
SMART_SQL_WORKFLOW_CONFIG_PATH=/app/assets/smart_sql_config.yaml
PROMPTS_PATH=/app/assets/prompts.yaml

# ============================================================================
# Source Download Configuration
# ============================================================================
SOURCE_DOWNLOAD_API_PATH_BASE=http://api-host:8700/api/v1/download
```

### 2. Prepare Assets Folder

Create the `assets` folder with required configuration and cache files:

```bash
mkdir -p assets
```

The assets folder must contain:

1. **Configuration Files** (YAML):
   - `agentic_rag_config.yaml` - Default RAG workflow configuration
   - `smart_sql_config.yaml` - SQL workflow configuration
   - `prompts.yaml` - LLM system prompts and templates

2. **Cache Files** (JSON):
   - `schema_cache.json` - Cached SQL database schema (generated from `SQL_REQUIRED_TABLES`)

#### Creating `schema_cache.json`

The schema cache is crucial for SQL query performance. It should contain the structure of your SQL database tables:

```json
{
  "table1": {
    "columns": [
      {
        "name": "column_name",
        "type": "varchar",
        "nullable": true
      }
    ]
  }
}
```

**Note**: This file is typically generated by introspecting your SQL database. If not present, the system will attempt to generate it at runtime (requires SQL write permissions).

#### Configuration File Examples

The workflow configuration files control how the RAG and SQL workflows behave. Refer to existing config files in the assets folder for the specific format and available parameters.

## Installation and Running

### Local Development Setup

1. **Create Python Virtual Environment**:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Environment**:
   - Copy the `.env` template above and populate with your service credentials
   - Ensure all external services (Weaviate, MongoDB, SQL Server) are accessible
   - Verify the assets folder contains all required configuration files

4. **Run Locally**:
```bash
# Start FastAPI application with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the default port from .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8700
```

The API will be available at:
- FastAPI Docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Docker Deployment

1. **Build Docker Images**:
```bash
# Build the main FastAPI application
docker build -t agentic_rag:1.0.0 -f Dockerfile.Base .

# Build the Weaviate UI (optional)
docker build -t weaviate_ui:1.0.0 -f weaviate_ui/Dockerfile weaviate_ui
```

2. **Start Services with Docker Compose**:
```bash
# Start all services in the background
docker-compose up -d

# View logs in real-time
docker-compose logs -f app

# View logs for specific service
docker-compose logs -f weaviate_ui

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

3. **Access Services**:
   - FastAPI Application: http://localhost:8700 (or configured APP_PORT)
   - API Documentation: http://localhost:8700/docs
   - Weaviate UI: http://localhost:8501 (or configured WEAVIATE_UI_PORT)
   - Weaviate Direct: http://weaviate-host:8100 (external service)

## API Usage

### 1. Agentic RAG Query

Send a natural language query to be processed by the RAG workflow:

```http
POST /api/v1/query
Content-Type: application/json

{
    "message": "What are the main rules?",
    "collection": "my_collection_name",
    "top_k": 3,
    "use_local_embedding": false
}
```

**Parameters**:
- `message` (required): Natural language question
- `collection` (required): Weaviate collection name to search in
- `top_k` (optional): Number of documents to retrieve (default: 3)
- `use_local_embedding` (optional): Use local embeddings instead of API (default: false)

**Example using curl**:
```bash
curl -X POST "http://localhost:8700/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What are the rules?",
       "collection": "my_collection",
       "top_k": 3
     }'
```

**Response**:
```json
{
  "answer": "The main rules are...",
  "sources": [
    {
      "filename": "document1.pdf",
      "download_link": "/api/v1/download/document1.pdf"
    }
  ],
  "metadata": {}
}
```

### 2. SQL Query Endpoint (Optional)

Convert natural language to SQL and execute queries (if `SQL_ENDPOINT_ENABLED=true`):

```http
POST /api/v1/sql/query
Content-Type: application/json

{
    "message": "Show all orders from January 2024",
    "use_cache": true
}
```

**Parameters**:
- `message` (required): Natural language query description
- `use_cache` (optional): Use cached schema for faster execution (default: true)

**Example using curl**:
```bash
curl -X POST "http://localhost:8700/api/v1/sql/query" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Show me all records from this year",
       "use_cache": true
     }'
```

### 3. Source Document Download

Download source documents referenced in responses:

```http
GET /api/v1/download/{filename}
```

**Features**:
- Efficient streaming (minimal memory usage)
- UTF-8 filename support (Persian/Arabic text)
- Automatic content-type detection
- Proper browser download headers

**Example**:
```bash
curl -X GET "http://localhost:8700/api/v1/download/document_name.pdf" \
     -o downloaded_file.pdf
```

## Workflow Architecture

The system uses LangGraph to orchestrate complex workflows:

### Agentic RAG Workflow
1. **Extract Keywords**: Parse the user query for search terms
2. **Retrieve Documents**: Query Weaviate for relevant documents
3. **Grade Documents**: Assess document relevance to the query
4. **Detect Sources**: Identify source filenames for attribution
5. **Generate Answer**: Create comprehensive answer from retrieved context
6. **Source Attribution**: Generate download links for source documents
7. **Return Results**: Merge and deduplicate results

### Smart SQL Workflow
1. **Decision Point**: Determine if query is SQL-suitable
2. **SQL Generation**: Convert natural language to SQL query
3. **Schema Caching**: Use cached schema for query optimization
4. **Execute Query**: Run SQL against the database
5. **Generate Answer**: Format results in natural language
6. **Return Results**: Return structured query results

Both workflows are configurable via YAML files in the `assets` folder.

## Troubleshooting

### Connection Issues

**Weaviate Connection Error**:
- Verify `WEAVIATE_HOST` and `WEAVIATE_PORT` are correct
- Check network connectivity to Weaviate server
- Verify `WEAVIATE_USER_KEY` authentication credentials
- Test with: `curl http://WEAVIATE_HOST:WEAVIATE_PORT/v1/well-known/ready`

**MongoDB Connection Error**:
- Verify `MONGODB_URI` format and credentials
- Check if MongoDB is running and accessible
- Verify username/password in `MONGODB_URI` matches `MONGODB_INITDB_DEV_USERNAME/PASSWORD`
- Test with: `mongosh "mongodb://user:pass@host:port"`

**SQL Server Connection Error**:
- Verify `SQL_HOST`, `SQL_PORT`, `SQL_USER`, and `SQL_PASS` are correct
- Ensure SQL Server is running and accessible
- For special characters in password, use URL encoding (e.g., `@` → `%40`)
- Check firewall rules allowing connection to SQL port
- Verify `SQL_DB` database exists and user has permissions

### LLM and Embedding Issues

**API Key Error**:
- Verify `API_KEY` is valid for chosen provider (OpenRouter, AvalAI, etc.)
- Check that API key hasn't expired or been revoked
- Ensure account has sufficient credits/quota

**Embedding Model Error**:
- Verify `EMBEDDING_URL` and `EMBEDDING_MODEL` are correct
- Check embedding service is running and accessible
- Test with: `curl http://EMBEDDING_URL/v1/models`

### Workflow Configuration Issues

**Missing Configuration Files**:
- Ensure `assets` folder exists with all required YAML files
- Verify paths in `.env` match actual file locations
- Check file permissions (readable by application)

**Schema Cache Issues**:
- If SQL queries fail, verify `schema_cache.json` contains correct table definitions
- Ensure `SQL_REQUIRED_TABLES` matches tables in schema cache
- For missing schema, regenerate from SQL database

### Docker-Specific Issues

**Port Already in Use**:
```bash
# Find process using port
lsof -i :8700

# Change port in .env
APP_PORT=8701

# Restart services
docker-compose up -d
```

**Services Won't Start**:
```bash
# Check container logs
docker-compose logs app
docker-compose logs weaviate_ui

# Verify environment file
cat .env | grep -E "^[A-Z_]+=.*" | head -20
```

**Permission Denied on assets**:
```bash
# Fix folder permissions
chmod 755 assets
chmod 644 assets/*
```

## Development Guide

### Project Dependencies

Key dependencies:
- **FastAPI**: Web framework
- **LangGraph**: Workflow orchestration
- **Weaviate**: Vector store operations
- **PyMongo**: MongoDB client
- **pyodbc/pymysql**: SQL database connectivity
- **OpenAI/LangChain**: LLM integrations

### Adding New Workflow Nodes

1. Create new node file in `app/workflows/nodes/`
2. Implement node function with proper state handling
3. Register node in workflow graph (`app/workflows/graph.py`)
4. Update workflow config YAML if parameters needed

### Modifying Workflow Configuration

Edit YAML files in `assets/` folder to adjust:
- Node parameters and thresholds
- Routing logic in decision points
- Prompt templates and system messages
- Embedding and retrieval settings

### Testing Locally

```bash
# Run with verbose logging
LOGLEVEL=DEBUG uvicorn app.main:app --reload

# Test specific endpoint
python -m pytest tests/ -v

# Check code quality
pylint app/

# Type checking
mypy app/
```

## Contributing

1. Create a new branch for your feature: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Ensure all dependencies are documented in `requirements.txt`
4. Update this README if adding new features or configuration options
5. Submit a pull request with clear description of change