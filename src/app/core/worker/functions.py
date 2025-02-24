import asyncio
import logging

import uvloop
from arq.worker import Worker

from src.app.core.config import settings
from src.app.core.utils.inference import (
    transcribe_audio_file,
    ollama_llm,
    llm_impressions_cleanup,
)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    # ctx["db"] = await anext(async_get_db())  # to use db in async call
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    # await ctx["db"].close() # to use db in async call
    logging.info("Worker end")


# --------- chained tasks ----------


async def transcribe_findings(ctx: Worker, req_body, audio_file) -> str:
    # transcribe audio file
    audio_text = await transcribe_audio_file(settings.MODELS["whisper"], audio_file)
    print("audio_text", audio_text)

    # call llm
    updated_text = await ollama_llm(
        prev_diagnosis=req_body["curr_text"],
        user_prompt=audio_text,
    )
    print("updated_text", updated_text)

    return updated_text


async def transcribe_impressions(ctx: Worker, audio_file: str) -> str:
    audio_text = await transcribe_audio_file(settings.MODELS["whisper"], audio_file)
    print("audio_text", audio_text)

    updated_text = await llm_impressions_cleanup(audio_text)
    print("updated_text", updated_text)

    return updated_text
