import asyncio
import logging

import httpx
import numpy as np
import requests
import uvloop
from arq.worker import Worker
from pywhispercpp.model import Model

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

    # initialize models as this is a separate worker process and doesnt share
    # the context of the core fastapi lifecycle
    # Load the models
    settings.MODELS["whisper"] = Model("base.en")

    # --- Warm up the models

    # whisper warm up
    sample_rate = 16000  # Standard sample rate for Whisper
    duration = 3.0  # Duration in seconds
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a sine wave at 440 Hz (A4 note)
    dummy_audio = np.sin(2 * np.pi * 440 * t)
    # Add some noise to make it more realistic
    dummy_audio += 0.5 * np.random.randn(len(dummy_audio))
    # Normalize to [-1, 1] range
    dummy_audio = dummy_audio / np.abs(dummy_audio).max()
    # Reshape to match expected format (batch_size, audio_length)
    dummy_audio = dummy_audio.reshape(1, -1)
    settings.MODELS["whisper"].transcribe(dummy_audio)


async def shutdown(ctx: Worker) -> None:
    # await ctx["db"].close() # to use db in async call
    logging.info("Worker end")
    settings.MODELS.clear()


# --------- chained tasks ----------
async def transcribe_findings(ctx: Worker, req_body, audio_file) -> str:
    # transcribe audio file
    audio_text = await transcribe_audio_file(settings.MODELS["whisper"], audio_file)

    if settings.ENVIRONMENT != "local":
        # call llm
        updated_text = await ollama_llm(
            prev_diagnosis=req_body["curr_text"],
            user_prompt=audio_text,
        )
        print("updated_text", updated_text)

        return updated_text

    return audio_text


async def transcribe_impressions(ctx: Worker, audio_file: str) -> str:
    audio_text = await transcribe_audio_file(settings.MODELS["whisper"], audio_file)
    print("audio_text", audio_text)

    if settings.ENVIRONMENT != "local":
        updated_text = await llm_impressions_cleanup(audio_text)
        print("updated_text", updated_text)

        return updated_text

    return audio_text
