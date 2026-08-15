# Mini RAG API

Minimal production-oriented Retrieval-Augmented Generation (RAG) API built with
FastAPI, MongoDB, Qdrant local storage, and pluggable LLM providers.

The app can upload documents, split them into chunks, store metadata in MongoDB,
index embeddings in Qdrant, search indexed content, and generate answers from
retrieved context.

## Features

- FastAPI HTTP API with interactive Swagger docs.
- MongoDB storage for projects, uploaded assets, and processed chunks.
- Local Qdrant vector database persisted under `src/assets/database`.
- LLM provider abstraction for OpenAI and Cohere.
- File upload, processing, indexing, semantic search, and RAG answer endpoints.

## Project Structure

```text
.
├── docker/
│   ├── docker-compose.yml      # MongoDB service for local development
│   └── .env.example            # Docker environment template
├── src/
│   ├── main.py                 # FastAPI entry point
│   ├── helpers/                # App settings and MongoDB connection
│   ├── routes/                 # API routes and request schemas
│   ├── controllers/            # Upload, processing, project, and NLP logic
│   ├── models/                 # Database models and response enums
│   ├── stores/                 # LLM and vector DB providers
│   ├── assets/                 # Local uploaded files and vector DB data
│   ├── requirements.txt
│   └── .env.example            # Application environment template
└── README.md
```

## Requirements

- Python 3.11 or newer.
- Docker and Docker Compose for MongoDB.
- An OpenAI or Cohere API key.

## Setup

Create and activate a Python environment:

```bash
conda create -n mini-rag python=3.11
conda activate mini-rag
```

Install dependencies:

```bash
python -m pip install -r src/requirements.txt
```

Create local environment files:

```bash
cp src/.env.example src/.env
cp docker/.env.example docker/.env
```

Update `src/.env` with your LLM provider, model IDs, and database URL. Update
`docker/.env` with your local MongoDB credentials.

## Environment Variables

The application reads configuration from `src/.env`.

| Variable | Description |
| --- | --- |
| `APP_NAME` | Application name shown in config. |
| `APP_VERSION` | Application version. |
| `FILE_ALLOWED_TYPES` | JSON list of allowed upload MIME types. |
| `FILE_MAX_SIZE` | Maximum upload size in MB. |
| `FILE_DEFAULT_CHUNK_SIZE` | Streaming upload chunk size in bytes. |
| `MONGODB_URL` | MongoDB connection string. |
| `MONGODB_DATABASE` | MongoDB database name. |
| `GENERATION_BACKEND` | Generation provider: `OPENAI` or `COHERE`. |
| `EMBEDDING_BACKEND` | Embedding provider: `OPENAI` or `COHERE`. |
| `OPENAI_API_KEY` | OpenAI API key when using OpenAI. |
| `OPENAI_API_URL` | OpenAI-compatible API base URL. |
| `COHERE_API_KEY` | Cohere API key when using Cohere. |
| `GENERATION_MODEL_ID` | Chat/generation model ID. |
| `EMBEDDING_MODEL_ID` | Embedding model ID. |
| `EMBEDDING_MODEL_SIZE` | Embedding vector dimension. |
| `INPUT_DEFAULT_MAX_CHARACTERS` | Maximum input characters sent to the LLM. |
| `GENERATION_DEFAULT_MAX_TOKENS` | Maximum generation output tokens. |
| `GENERATION_DEFAULT_TEMPERATURE` | Default generation temperature. |
| `VECTOR_DB_BACKEND` | Vector DB provider. Currently `QDRANT`. |
| `VECTOR_DB_DISTANCE_METHOD` | Qdrant distance method: `COSINE` or `DOT`. |
| `VECTOR_DB_PATH` | Local Qdrant database directory name. |
| `PRIMARY_LANG` | Primary prompt template language. |
| `DEFAULT_LANG` | Fallback prompt template language. |

## Run MongoDB

From the project root:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml up -d
```

Stop MongoDB:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml down
```

To remove the local MongoDB volume as well:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml down -v
```

## Run the API

From `src`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Open the API documentation:

- Swagger UI: <http://localhost:5000/docs>
- ReDoc: <http://localhost:5000/redoc>

## Main API Flow

Use the same `project_id` across the full workflow.

1. Upload a file:

   ```http
   POST /api/v1/data/upload/{project_id}
   ```

   Send a multipart form field named `file`.

2. Process uploaded files into chunks:

   ```http
   POST /api/v1/data/process/{project_id}
   ```

   Example body:

   ```json
   {
     "file_id": null,
     "chunk_size": 100,
     "overlap_size": 20,
     "do_reset": 0
   }
   ```

3. Push chunks to the vector index:

   ```http
   POST /api/v1/index/push/{project_id}
   ```

   Example body:

   ```json
   {
     "do_reset": 0
   }
   ```

4. Search indexed content:

   ```http
   POST /api/v1/index/search/{project_id}
   ```

   Example body:

   ```json
   {
     "text": "What is this document about?",
     "limit": 5
   }
   ```

5. Generate a RAG answer:

   ```http
   POST /api/v1/index/answer/{project_id}
   ```

   Example body:

   ```json
   {
     "text": "Summarize the key points.",
     "limit": 5
   }
   ```

## Local Data

Runtime data is written under `src/assets`:

- `src/assets/files`: uploaded project files.
- `src/assets/database`: local Qdrant data.

These paths are ignored by Git.

## Troubleshooting

- If the API cannot connect to MongoDB, make sure the Docker service is running
  and `MONGODB_URL` matches the credentials in `docker/.env`.
- If indexing or answering fails, verify `GENERATION_BACKEND`,
  `EMBEDDING_BACKEND`, API keys, model IDs, and `EMBEDDING_MODEL_SIZE`.
- If uploads fail with file type errors, check `FILE_ALLOWED_TYPES` in `src/.env`.
