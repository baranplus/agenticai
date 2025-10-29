# Agentic RAG System

This project implements an Agentic RAG (Retrieval-Augmented Generation) system using FastAPI and Weaviate. The system features a sophisticated agent-based architecture for improved query processing and response generation.

## Features

- Agent-based RAG architecture with multiple specialized nodes:
  - Question rewriting for improved retrieval
  - Document grading for relevance assessment
  - Source attribution with downloadable references
  - Natural language to SQL query conversion
- Persian (Farsi) language support with proper text handling
- Integrated document storage and retrieval:
  - Weaviate for vector search
  - MongoDB for source document storage
  - SQL Server for structured data querying
  - Downloadable source documents with UTF-8 support
- Docker containerization for easy deployment
- Authentication for data stores
- SQL schema caching for optimized query performance
- Interactive Weaviate UI for:
  - Visual exploration of document collections
  - Advanced hybrid search capabilities
  - Source-based filtering and statistics
  - Document content and metadata viewing

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
│   │   ├── rewrite_question_node.py  # Question optimization
│   │   ├── retriever_node.py        # Document retrieval
│   │   ├── grade_document_node.py   # Relevance assessment
│   │   ├── sourcing_node.py        # Source attribution and links
│   │   ├── sql_node.py             # SQL query handling
│   │   └── generate_answer_node.py  # Answer generation
│   ├── db/             # Database implementations
│   │   ├── vector_store.py         # Weaviate integration
│   │   ├── client.py              # MongoDB integration
│   │   ├── sql_client.py          # SQL Server integration
│   │   └── collection.py          # Collection management
│   ├── llm/            # LLM configurations and templates
│   ├── routers/        # FastAPI routes
│   │   ├── agentic_rag.py        # Main query endpoint
│   │   ├── download_source.py    # Source file downloads
│   │   └── smart_sql.py         # SQL query handling
│   ├── schema/         # Data models and validation
│   └── utils/          # Utility functions
├── assets/            # Required folder for SQL schema cache
│   └── schema_cache.json  # SQL database schema cache
├── weaviate_ui/       # Interactive UI for Weaviate
│   ├── app.py         # Streamlit application
│   ├── Dockerfile     # UI service container
│   └── requirements.txt # UI dependencies
├── docker-compose.yaml
├── Dockerfile.Base
└── requirements.txt
```

## Environment Setup

1. Create a `.env` file in the project root with the following structure:

```env
# Docker Services
APP_IMAGE=agentic_rag:1.0.0
WEAVIATE_UI_IMAGE=weaviate_ui:1.0.0
APP_PORT=8700
WEAVIATE_UI_PORT=8501

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

# MongoDB Configuration
MONGODB_URI=mongodb://host:port
MONGODB_DB_NAME=db name
MONGODB_COLLECTION_SOURCE_FILES=collection source files name
MONGO_INITDB_DEV_USERNAME=root user
MONGO_INITDB_DEV_PASSWORD=root password

# Source Download API Configuration
SOURCE_DOWNLOAD_API_PATH_BASE=http://host:port/api/v1/download

## SQL Server Configuration
SQL_HOST=sql server host
SQL_PORT=sql server port
SQL_USER=sql user
SQL_PASS=sql password
SQL_DB=sql database
SQL_METADATA_CACHE_PATH=/path/to/cached/schema/json/in/container
SQL_REQUIRED_TABLE=needed tables separated by commas, EG -> table1,table2
```

## Assets Setup

1. Create an `assets` folder in the project root if it doesn't exist:
```bash
mkdir -p assets
```

2. If you have a cached SQL database schema, place it in the assets folder as `schema_cache.json`. This file should match the path specified in `SQL_METADATA_CACHE_PATH` environment variable. The schema cache helps optimize SQL query performance and is required for SQL-related features.

## Installation and Running

1. First, build the Docker images:
```bash
# Build the FastAPI application image
docker build -t agentic_rag:1.0.0 -f Dockerfile.Base .

# Build the Weaviate UI image
docker build -t weaviate_ui:1.0.0 -f weaviate_ui/Dockerfile weaviate_ui
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
   - Weaviate UI: http://host:8501 (A user-friendly interface for searching and analyzing Weaviate collections)

## API Usage

### Main Query Endpoint
```http
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

### SQL Query Endpoint
```http
POST /api/v1/sql/query

{
    "message": "Your natural language query",
    "use_cache": true
}
```

Example using curl:
```bash
curl -X POST "http://localhost:8700/api/v1/sql/query" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Show me all orders from last month",
           "use_cache": true
         }'
```

### Source Document Download
The system provides downloadable links to source documents referenced in responses:

```http
GET /api/v1/download/{filename}
```

Features:
- Streams file content for efficient memory usage
- Supports UTF-8 filenames (Persian/Arabic text)
- Automatic content-type detection
- Proper file attachment headers for browser downloads

The download URLs are automatically included in query responses when sources are referenced. Each source reference includes:
- A superscript number (e.g., ¹, ², ³)
- A clickable link to download the source document
- Automatic deduplication of repeated sources

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
   - Verify MongoDB authentication settings (username, password, and database)
   - Check Weaviate API key configuration

2. If source downloads fail:
   - Verify `SOURCE_DOWNLOAD_API_PATH_BASE` is correctly set in `.env`
   - Check MongoDB connection and collection name
   - Ensure the files were properly uploaded to MongoDB
   - For Persian/Arabic filenames, verify UTF-8 encoding is preserved

3. If the services don't start:
   - Check if the required ports are available
   - Verify Docker and Docker Compose installation
   - Check the logs using `docker-compose logs`
   - Ensure all required environment variables are set

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details