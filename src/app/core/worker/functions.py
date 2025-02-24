import asyncio
import logging

import uvloop
from arq.worker import Worker

from ...core.db.database import async_get_db

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)

    # to use db crud on async call
    # db = ctx["db"]
    # post = crud_posts.get(db=db, schema_to_select=PostRead, id=post_id)

    return f"Task {name} is complete!"


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    # ctx["db"] = await anext(async_get_db())  # to use db in async call
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    # await ctx["db"].close() # to use db in async call
    logging.info("Worker end")
