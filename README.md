
# to migrate models to pg 

```sh
alembic revision --autogenerate -m " ... msg ..." && alembic upgrade head
```



### Project Structure

```sh
.
├── Dockerfile                        # Dockerfile for building the application container.
├── docker-compose.yml                # Docker Compose file for defining multi-container applications.
├── README.md                         # Project README providing information and instructions.
|
├── tests                             # Unit and integration tests for the application.
│   ├── __init__.py
│   ├── conftest.py                   # Configuration and fixtures for pytest.
│   ├── helper.py                     # Helper functions for tests.
│   └── test_user.py                  # Test cases for user-related functionality.
│
└── src                               # Source code directory.
    ├── __init__.py                   # Initialization file for the src package.
    ├── alembic.ini                   # Configuration file for Alembic (database migration tool).
    ├── poetry.lock                   # Poetry lock file specifying exact versions of dependencies.
    │
    ├── app                           # Main application directory.
    │   ├── __init__.py               # Initialization file for the app package.
    │   ├── main.py                   # Main entry point of the FastAPI application.
    │   │
    │   │
    │   ├── api                       # Folder containing API-related logic.
    │   │   ├── __init__.py
    │   │   ├── dependencies.py       # Defines dependencies for use across API endpoints.
    │   │   │
    │   │   └── v1                    # Version 1 of the API.
    │   │       ├── __init__.py
    │   │       ├── login.py          # API route for user login.
    │   │       ├── logout.py         # API route for user logout.
    │   │       ├── rate_limits.py    # API routes for rate limiting functionalities.
    │   │       ├── tasks.py          # API routes for task management.
    │   │       ├── tiers.py          # API routes for user tier functionalities.
    │   │       └── users.py          # API routes for user management.
    │   │
    │   ├── core                      # Core utilities and configurations for the application.
    │   │   ├── __init__.py
    │   │   ├── config.py             # Configuration settings for the application.
    │   │   ├── logger.py             # Configuration for application logging.
    │   │   ├── schemas.py            # Pydantic schemas for data validation.
    │   │   ├── security.py           # Security utilities, such as password hashing.
    │   │   ├── setup.py              # Setup file for the FastAPI app instance.
    │   │   │
    │   │   ├── db                    # Core Database related modules.
    │   │   │   ├── __init__.py
    │   │   │   ├── database.py       # Database connectivity and session management.
    │   │   │   ├── models.py         # Core Database models.
    │   │   │
    │   │   ├── exceptions            # Custom exception classes.
    │   │   │   ├── __init__.py
    │   │   │   ├── cache_exceptions.py   # Exceptions related to cache operations.
    │   │   │   └── http_exceptions.py    # HTTP-related exceptions.
    │   │   │
    │   │   ├── utils                 # Utility functions and helpers.
    │   │   │   ├── __init__.py
    │   │   │   ├── cache.py          # Cache-related utilities.
    │   │   │   ├── queue.py          # Utilities for task queue management.
    │   │   │   └── rate_limit.py     # Rate limiting utilities.
    │   │   │
    │   │   └── worker                # Worker script for background tasks.
    │   │       ├── __init__.py
    │   │       ├── settings.py       # Worker configuration and settings.
    │   │       └── functions.py      # Async task definitions and management.
    │   │
    │   ├── crud                      # CRUD operations for the application.
    │   │   ├── __init__.py
    │   │   ├── crud_base.py          # Base class for CRUD operations.
    │   │   ├── crud_rate_limit.py    # CRUD operations for rate limiting.
    │   │   ├── crud_tier.py          # CRUD operations for user tiers.
    │   │   ├── crud_users.py         # CRUD operations for users.
    │   │   ├── crud_token_blacklist.py  # CRUD operations for token blacklist.
    │   │   └── helper.py             # Helper functions for CRUD operations.
    
    │   │
    │   ├── logs                      # Directory for log files.
    │   │   └── app.log               # Log file for the application.
    │   │
    │   ├── middleware                # Middleware components for the application.
    │   │   └── client_cache_middleware.py  # Middleware for client-side caching.
    │   │
    │   └── models                    # SQLModel db and validation models for the application.
    │       ├── __init__.py
    │       ├── rate_limit.py         # SQLModel models for rate limiting.
    │       ├── tier.py               # SQLModel models for user tiers.
    │       └── user.py               # SQLModel models for users.
    │   │   └── token_blacklist.py  # Model for token blacklist functionality.
    │
    ├── migrations                    # Alembic migration scripts for database changes.
    │   ├── README
    │   ├── env.py                    # Environment configuration for Alembic.
    │   ├── script.py.mako            # Template script for Alembic migrations.
    │   │
    │   └── versions                  # Individual migration scripts.
    │       └── README.MD
    │
    └── scripts                       # Utility scripts for the application.
        ├── __init__.py
        ├── create_first_superuser.py # Script to create the first superuser.
        └── create_first_tier.py      # Script to create the first user tier.
```

### 5.8 Caching

The `cache` decorator allows you to cache the results of FastAPI endpoint functions, enhancing response times and reducing the load on your application by storing and retrieving data in a cache.

Caching the response of an endpoint is really simple, just apply the `cache` decorator to the endpoint function.

> \[!WARNING\]
> Note that you should always pass request as a variable to your endpoint function if you plan to use the cache decorator.

```python
...
from app.core.utils.cache import cache


@app.get("/sample/{my_id}")
@cache(key_prefix="sample_data", expiration=3600, resource_id_name="my_id")
async def sample_endpoint(request: Request, my_id: int):
    # Endpoint logic here
    return {"data": "my_data"}
```

The way it works is:

- the data is saved in redis with the following cache key: `sample_data:{my_id}`
- then the time to expire is set as 3600 seconds (that's the default)

Another option is not passing the `resource_id_name`, but passing the `resource_id_type` (default int):

```python
...
from app.core.utils.cache import cache


@app.get("/sample/{my_id}")
@cache(key_prefix="sample_data", resource_id_type=int)
async def sample_endpoint(request: Request, my_id: int):
    # Endpoint logic here
    return {"data": "my_data"}
```

In this case, what will happen is:

- the `resource_id` will be inferred from the keyword arguments (`my_id` in this case)
- the data is saved in redis with the following cache key: `sample_data:{my_id}`
- then the the time to expire is set as 3600 seconds (that's the default)

Passing resource_id_name is usually preferred.

### More Advanced Caching

The behaviour of the `cache` decorator changes based on the request method of your endpoint.
It caches the result if you are passing it to a **GET** endpoint, and it invalidates the cache with this key_prefix and id if passed to other endpoints (**PATCH**, **DELETE**).

#### Invalidating Extra Keys

If you also want to invalidate cache with a different key, you can use the decorator with the `to_invalidate_extra` variable.

In the following example, I want to invalidate the cache for a certain `user_id`, since I'm deleting it, but I also want to invalidate the cache for the list of users, so it will not be out of sync.

```python
# The cache here will be saved as "{username}_posts:{username}":
@router.get("/{username}/posts", response_model=List[PostRead])
@cache(key_prefix="{username}_posts", resource_id_name="username")
async def read_posts(request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]):
    ...


...

# Invalidating cache for the former endpoint by just passing the key_prefix and id as a dictionary:
@router.delete("/{username}/post/{id}")
@cache(
    "{username}_post_cache",
    resource_id_name="id",
    to_invalidate_extra={"{username}_posts": "{username}"},  # also invalidate "{username}_posts:{username}" cache
)
async def erase_post(
    request: Request,
    username: str,
    id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    ...


# And now I'll also invalidate when I update the user:
@router.patch("/{username}/post/{id}", response_model=PostRead)
@cache("{username}_post_cache", resource_id_name="id", to_invalidate_extra={"{username}_posts": "{username}"})
async def patch_post(
    request: Request,
    username: str,
    id: int,
    values: PostUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    ...
```

> \[!WARNING\]
> Note that adding `to_invalidate_extra` will not work for **GET** requests.

#### Client-side Caching

For `client-side caching`, all you have to do is let the `Settings` class defined in `app/core/config.py` inherit from the `ClientSideCacheSettings` class. You can set the `CLIENT_CACHE_MAX_AGE` value in `.env,` it defaults to 60 (seconds).

### ARQ Job Queues

Depending on the problem your API is solving, you might want to implement a job queue. A job queue allows you to run tasks in the background, and is usually aimed at functions that require longer run times and don't directly impact user response in your frontend. As a rule of thumb, if a task takes more than 2 seconds to run, can be executed asynchronously, and its result is not needed for the next step of the user's interaction, then it is a good candidate for the job queue.

> [!TIP]
> Very common candidates for background functions are calls to and from LLM endpoints (e.g. OpenAI or Openrouter). This is because they span tens of seconds and often need to be further parsed and saved.

#### Background task creation

For simple background tasks, you can just create a function in the `app/core/worker/functions.py` file. For more complex tasks, we recommend you to create a new file in the `app/core/worker` directory.

```python
async def sample_background_task(ctx, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"
```

Then add the function to the `WorkerSettings` class `functions` variable in `app/core/worker/settings.py` to make it available to the worker. If you created a new file in the `app/core/worker` directory, then simply import this function in the `app/core/worker/settings.py` file:


 ```python
 from .functions import sample_background_task
 from .your_module import sample_complex_background_task

 class WorkerSettings:
     functions = [sample_background_task, sample_complex_background_task]
     ...
 ```

#### Add the task to an endpoint

Once you have created the background task, you can add it to any endpoint of your choice to be enqueued. 
The best practice is to enqueue the task in a **POST** endpoint, while having a 
**GET** endpoint to get more information on the task. For more details on how job results are handled,
check the [ARQ docs](https://arq-docs.helpmanual.io/#job-results).

```python
@router.post("/task", response_model=Job, status_code=201)
async def create_task(message: str):
    job = await queue.pool.enqueue_job("sample_background_task", message)
    return {"id": job.job_id}


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    job = ArqJob(task_id, queue.pool)
    return await job.info()
```

And finally run the worker in parallel to your fastapi application.

> [!IMPORTANT]
> For any change to the `sample_background_task` to be reflected in the worker, you need to restart the worker (e.g. the docker container).

If you are using `docker compose`, the worker is already running.
If you are doing it from scratch, run while in the `root` folder:

```sh
poetry run arq src.app.core.worker.settings.WorkerSettings
```

#### Database session with background tasks

With time your background functions will become 'workflows' increasing in complexity and requirements. Probably, you will need to use a database session to get, create, update, or delete data as part of this workflow.

To do this, you can add the database session to the `ctx` object in the `startup` and `shutdown` functions in `app/core/worker/functions.py`, like in the example below:

```python
from arq.worker import Worker
from ...core.db.database import async_get_db

async def startup(ctx: Worker) -> None:
    ctx["db"] = await anext(async_get_db())
    logging.info("Worker Started")

async def shutdown(ctx: Worker) -> None:
    await ctx["db"].close()
    logging.info("Worker end")
```

This will allow you to have the async database session always available in any background function and automatically close it on worker shutdown. Once you have this database session, you can use it as follows:

```python
from arq.worker import Worker

async def your_background_function(
    ctx: Worker,
    post_id: int,
    ...
) -> Any:
    db = ctx["db"]
    post = crud_posts.get(db=db, schema_to_select=PostRead, id=post_id)
    ...
```

> [!WARNING]
> When using database sessions, you will want to use Pydantic objects. However, these objects don't mingle well with the seralization required by ARQ tasks and will be retrieved as a dictionary.

### Running

If you are using docker compose, just running the following command should ensure everything is working:

```sh
docker compose up
```

If you are doing it from scratch, ensure your postgres and your redis are running, then
while in the `root` folder, run to start the application with uvicorn server:

```sh
poetry run uvicorn src.app.main:app --reload
```

And for the worker:

```sh
poetry run arq src.app.core.worker.settings.WorkerSettings
```


## Running in Production

### Uvicorn Workers with Gunicorn

In production you may want to run using gunicorn to manage uvicorn workers:

```sh
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Here it's running with 4 workers, but you should test it depending on how many cores your machine has.

To do this if you are using docker compose, just replace the comment:
This part in `docker-compose.yml`:

```YAML
# docker-compose.yml

# -------- replace with comment to run with gunicorn --------
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Should be changed to:

```YAML
# docker-compose.yml

# -------- replace with comment to run with uvicorn --------
# command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

And the same in `Dockerfile`:
This part:

```Dockerfile
# Dockerfile

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker". "-b", "0.0.0.0:8000"]
```

Should be changed to:

```Dockerfile
# Dockerfile

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker". "-b", "0.0.0.0:8000"]
```

> \[!CAUTION\]
> Do not forget to set the `ENVIRONMENT` in `.env` to `production` unless you want the API docs to be public.

### Running with NGINX

NGINX is a high-performance web server, known for its stability, rich feature set, simple configuration, and low resource consumption. NGINX acts as a reverse proxy, that is, it receives client requests, forwards them to the FastAPI server (running via Uvicorn or Gunicorn), and then passes the responses back to the clients.

To run with NGINX, you start by uncommenting the following part in your `docker-compose.yml`:

```python
# docker-compose.yml

...
# -------- uncomment to run with nginx --------
# nginx:
#   image: nginx:latest
#   ports:
#     - "80:80"
#   volumes:
#     - ./default.conf:/etc/nginx/conf.d/default.conf
#   depends_on:
#     - web
...
```

Which should be changed to:

```YAML
# docker-compose.yml

...
  #-------- uncomment to run with nginx --------
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./default.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
...
```

Then comment the following part:

```YAML
# docker-compose.yml

services:
  web:
    ...
    # -------- Both of the following should be commented to run with nginx --------
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    # command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Which becomes:

```YAML
# docker-compose.yml

services:
  web:
    ...
    # -------- Both of the following should be commented to run with nginx --------
    # command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    # command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Then pick the way you want to run (uvicorn or gunicorn managing uvicorn workers) in `Dockerfile`.
The one you want should be uncommented, comment the other one.

```Dockerfile
# Dockerfile

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker". "-b", "0.0.0.0:8000"]
```

And finally head to `http://localhost/docs`.

#### 6.2.1 One Server

If you want to run with one server only, your setup should be ready. Just make sure the only part that is not a comment in `default.conf` is:

```conf
# default.conf

# ---------------- Running With One Server ----------------
server {
    listen 80;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

So just type on your browser: `http://localhost/docs`.

#### 6.2.2 Multiple Servers

NGINX can distribute incoming network traffic across multiple servers, improving the efficiency and capacity utilization of your application.

To run with multiple servers, just comment the `Running With One Server` part in `default.conf` and Uncomment the other one:

```conf
# default.conf

# ---------------- Running With One Server ----------------
...

# ---------------- To Run with Multiple Servers, Uncomment below ----------------
upstream fastapi_app {
    server fastapi1:8000;  # Replace with actual server names or IP addresses
    server fastapi2:8000;
    # Add more servers as needed
}

server {
    listen 80;

    location / {
        proxy_pass http://fastapi_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

And finally, on your browser: `http://localhost/docs`.

> \[!WARNING\]
> Note that we are using `fastapi1:8000` and `fastapi2:8000` as examples, you should replace it with the actual name of your service and the port it's running on.