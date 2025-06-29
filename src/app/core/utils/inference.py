import asyncio

import httpx
import requests
from fastapi import HTTPException

llm_endpoint = "http://127.0.0.1:11434/api/chat"
# llm_model = "phi4:latest"
llm_model = "llama3.2:1b"


async def transcribe_audio_file(whisper_model, file_path: str) -> str:
    try:
        segments = await asyncio.to_thread(whisper_model.transcribe, file_path)

        all_text = ""
        for segment in segments:
            all_text += segment.text + " "

        return all_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


async def ollama_llm(prev_diagnosis: str, user_prompt: str) -> str | None:
    data = {
        "model": llm_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a radiologists typing assistant. "
                "You need to edit a new text against the previous provided one. Edit the "
                "prev_diagnosis to accommodate what the new_diagnosis wants to add. "
                "Maintain the structure of prev_diagnosis, just update the information from "
                "new_diagnosis into prev_diagnosis. Provide the result in the exact same "
                "format as the prev_diagnosis. If markdown characters \\n \\t are present return them as is."
                "There might be transcription errors in new_diagnosis due to misunderstanding. "
                "If words don't align with the context of radiology, edit them for what you see fit in context with the rest of the new_diagnosis."
                "Remember: provide the result in the exact same format as the prev_diagnosis. Avoid duplication.",
            },
            {
                "role": "user",
                "content": f"prev_diagnosis: {prev_diagnosis} \n\n new_diagnosis: {user_prompt}",
            },
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            llm_endpoint, headers={"Content-Type": "application/json"}, json=data
        )
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"HTTP error: {e}")
        return None


async def llm_impressions_cleanup(user_prompt: str) -> str | None:
    data = {
        "model": llm_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a radiologists typing assistant. "
                "You need to edit some transcribed text. There might be some typos. "
                "You need to modify the incoming_text in the context of radiology and update "
                "the provided prompt. Return text in the same format as the incoming_text, "
                "just edit it to take care of typos and conform to radiology domain. Avoid duplication.",
            },
            {
                "role": "user",
                "content": f"incoming_text:: {user_prompt}",
            },
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            llm_endpoint, headers={"Content-Type": "application/json"}, json=data
        )
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"HTTP error: {e}")
        return None
