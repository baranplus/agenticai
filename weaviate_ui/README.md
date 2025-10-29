# Weaviate Document Search UI

A Streamlit-based user interface for searching and analyzing documents stored in Weaviate vector database.

## Features

- Connect to any Weaviate instance with authentication
- Browse collections and their statistics
- Advanced document search capabilities:
  - Hybrid search (combining vector and keyword search)
  - Source-based filtering
  - Keyword combinations
  - Adjustable search parameters
- Collection statistics:
  - Total document count
  - Documents per source
  - Sample document previews
- Document display:
  - Content preview
  - Metadata information
  - Technical details (UUID, scores, distances)

## Environment Variables

Create a `.env` file with the following variables:

```env
# Weaviate Connection Settings
WEAVIATE_HOST=your_weaviate_host
WEAVIATE_PORT=your_weaviate_port
WEAVIATE_USER_KEY=your_weaviate_api_key
HYBRID_SEARCH_ALPHA=0.25  # Adjust this value between 0 and 1

# Docker Settings
WEAVIATE_UI_IMAGE=weaviate-ui:latest  # The image name and tag for the UI
WEAVIATE_UI_PORT=8501  # The port to expose the UI on your host machine
```

## Local Development

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Docker Deployment

### Build and Run with Docker

1. First, build the Docker image:
```bash
docker build -t weaviate-ui:latest .
```

2. Verify that your `.env` file contains the correct environment variables:
```bash
WEAVIATE_UI_IMAGE=weaviate-ui:latest
WEAVIATE_UI_PORT=8501
# ... other variables ...
```

3. Start the application with Docker Compose:
```bash
docker compose up -d
```

4. Access the UI at `http://localhost:8501` (or whatever port you specified in WEAVIATE_UI_PORT)

5. View the logs:
```bash
docker compose logs -f
```

6. Stop the application:
```bash
docker compose down
```

### Alternative Manual Deployment

1. Build the image:
```bash
docker build -t weaviate-ui .
```

2. Run the container:
```bash
docker run -d -p 8501:8501 --env-file .env weaviate-ui
```

## Usage

1. Connect to Weaviate:
   - Enter your Weaviate host, port, and API key
   - Click "Connect"

2. View Collection Statistics:
   - Select a collection
   - Optionally filter by source
   - Click "Show Collection Stats"

3. Search Documents:
   - Enter your search query
   - Adjust number of results and hybrid search alpha
   - Optionally filter by source
   - Click "Search"

## Requirements

- Python 3.12+
- Streamlit
- Weaviate Client
- Python-dotenv

For detailed requirements, see `requirements.txt`.