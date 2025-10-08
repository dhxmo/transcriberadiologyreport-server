# Radiology Retr Transcription 

FastAPI-based radiology transcription server that uses Whisper for audio transcription and local LLM (Ollama) for text refinement. The application processes audio recordings from radiologists and generates structured radiology reports with real-time WebSocket communication.

## Common Commands

### Development
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem
```

### Database Migrations
```bash
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

### Background Worker
```bash
poetry run arq src.app.core.worker.settings.WorkerSettings
```

### Testing
```bash
pytest
```

### Docker
```bash
docker compose up
```

## Architecture

### Core Design Pattern: Async-First with Background Processing

The application follows a separation between API request handling and compute-intensive tasks:

1. **API Layer** (`src/app/api/v1/`) - FastAPI endpoints accept requests and enqueue background jobs
2. **Worker Layer** (`src/app/core/worker/`) - ARQ workers execute ML inference tasks (Whisper transcription, LLM processing) in parallel processes
3. **Communication Layer** - WebSocket connections handle real-time audio streaming

### Key Architectural Decisions

**Parallel Process Design for ML Models**
- Whisper and LLM models live in worker processes, NOT in the FastAPI lifecycle
- Models are initialized in `worker/functions.py:startup()` and warmed up with dummy data
- The main FastAPI app remains lightweight; all inference happens via ARQ job queue
- This prevents model loading from blocking API responses

**WebSocket Audio Streaming Pattern**
- Each WebSocket connection generates a UUID for the recording session
- Audio chunks are written directly to disk as they arrive via `aiofiles`
- The UUID is sent back to client immediately upon connection
- File path: `{MEDIA_DIR_PATH}/{uuid}.webm`
- Reset functionality truncates the file pointer without disconnecting

**Two-Stage Transcription Workflow**
1. **Findings transcription**: `transcribe_findings` takes `curr_text` + audio → calls Whisper → calls `ollama_llm` to merge new text with existing diagnosis
2. **Impressions transcription**: `transcribe_impressions` takes audio → calls Whisper → calls `llm_impressions_cleanup` for typo correction

**Task Enqueueing Pattern**
- Endpoints in `api/v1/tasks.py` accept requests with `audio_uuid`
- They enqueue jobs to ARQ: `queue.pool.enqueue_job("function_name", args...)`
- Return job ID immediately for client polling
- Client polls `/tasks/task/{task_id}` to get status/results

**Sync HTTP Calls in Async Context**
- LLM calls in `utils/inference.py` use `requests.post()` (sync) despite being in async functions
- This is intentional for the local Ollama endpoint which doesn't benefit from async overhead
- Note comment in recent commits about testing async HTTP with httpx

**Cache Decorator Design**
- The `@cache` decorator from `core/utils/cache.py` provides Redis-backed caching
- GET requests: check cache → call function if miss → store result
- Non-GET requests: invalidate cache for the resource
- Supports dynamic key prefixes with `{variable}` syntax
- Can invalidate extra keys via `to_invalidate_extra` parameter
- Requires `Request` as first parameter in endpoint functions

**Settings Architecture**
- Multiple settings classes inherit into single `Settings` class
- Environment variables loaded via `starlette.Config` from `.env`
- `settings.MODELS` dict stores ML models (populated in worker, not main app)

**Database Session Management**
- Uses SQLModel (Pydantic + SQLAlchemy)
- Async engine with asyncpg driver
- Database sessions available in workers via `ctx["db"]` if needed (currently commented out)

**Authentication via Clerk**
- Clerk session tokens validated in dependencies (`api/dependencies.py`)
- Separate dependencies for HTTP (`get_current_user`) and WebSocket (`ws_get_current_user`)
- Uses `asyncio.run_in_executor` to call sync Clerk SDK in async context

## Code Style and Abstractions

### Consistent Patterns

**Path Construction**
- Always use `settings.MEDIA_DIR_PATH` or `settings.MEDIA_AWS_DIR_PATH`
- Construct paths as: `f"{settings.MEDIA_DIR_PATH}/{uuid}.webm"`

**Error Handling in Inference**
- Wrap model calls in try/except
- Raise `HTTPException` with descriptive messages
- Print errors for debugging (LLM functions return `None` on error)

**Background Function Signature**
- First parameter is always `ctx: Worker`
- Return type annotation required
- Must be added to `WorkerSettings.functions` list

**Async Operations**
- Use `asyncio.to_thread()` for CPU-bound operations (e.g., Whisper transcription)
- Use `aiofiles` for file I/O in async contexts
- Use `run_in_executor` for sync SDK calls (Clerk)

**Model Warmup**
- Generate realistic dummy data (not just zeros)
- Whisper: 3-second sine wave at 440 Hz with noise
- Run inference once during worker startup

**Redis Connections**
- Cache: `redis.asyncio` with connection pool
- Queue: ARQ with `RedisSettings`
- Separate Redis instances for cache vs queue (different ports)

**Logging**
- Use Python's built-in `logging` module
- Worker uses structured logging with timestamps
- Print statements acceptable for debugging in development

### Anti-Patterns to Avoid

- Don't load ML models in FastAPI lifespan (keep them in workers)
- Don't use sync blocking calls in main API thread
- Don't forget to add new background tasks to `WorkerSettings.functions`
- Don't use placeholders in cache key prefixes without understanding format logic
- Don't commit with `.reload` flag in production Docker configs

## Important File Locations

- **Main entry**: `src/app/main.py`
- **API routes**: `src/app/api/v1/`
- **Worker tasks**: `src/app/core/worker/functions.py`
- **Worker config**: `src/app/core/worker/settings.py`
- **ML inference**: `src/app/core/utils/inference.py`
- **Cache decorator**: `src/app/core/utils/cache.py`
- **WebSocket manager**: `src/app/core/ws_connection_manager.py`
- **Config**: `src/app/core/config.py`
- **Database models**: `src/app/core/db/models.py`
- **Pydantic models**: `src/app/models/`
- **Template**: `assets/findings_template.json`

## Environment-Specific Behavior

- `ENVIRONMENT=local`: Docs accessible at `/docs` and `/redoc`
- `ENVIRONMENT=production`: API docs disabled (endpoints return None)
- CORS configured to allow all origins (development setting)

## Testing

- Test client fixture in `tests/conftest.py`
- Uses FastAPI's `TestClient` with session scope
- Helper functions in `tests/helper.py`
