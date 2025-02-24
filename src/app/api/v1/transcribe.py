import json

import aiofiles
from fastapi import APIRouter, Request, WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect

from ...core.config import settings
from ...core.inference import transcribe_audio_file, ollama_llm, llm_impressions_cleanup
from ...core.ws_connection_manager import ConnectionManager

router = APIRouter(tags=["transcribe"])


@router.get("/get-template")
def get_template(modality: str, organ: str):
    # TODO: check if there is any template entry in the user_id, modality, organ table
    # TODO: if yes pull that and send.
    # TODO ELSE:
    with open(settings.COMMON_TEMPLATE_PATH, "r") as f:
        json_data = json.load(f)

    return {"findings_template": json_data[modality.lower()][organ.lower()]}


@router.post("/update-text")
async def update_text(request: Request):
    try:
        req_body = await request.json()

        audio_file = f"{settings.MEDIA_DIR_PATH}/{str(req_body['audio_uuid'])}.webm"

        # transcribe audio file
        audio_text = transcribe_audio_file(settings.MODELS["whisper"], audio_file)
        print("audio_text", audio_text)

        # call llm
        updated_text = ollama_llm(
            prev_diagnosis=req_body["curr_text"],
            user_prompt=audio_text,
        )
        print("updated_text", updated_text)

        return {"updated_text": updated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/transcribe-impression")
async def transcribe_impression(request: Request):
    req_body = await request.json()

    audio_file = f"{settings.MEDIA_DIR_PATH}/{str(req_body['audio_uuid'])}.webm"
    audio_text = transcribe_audio_file(settings.MODELS["whisper"], audio_file)
    print("audio_text", audio_text)

    updated_text = llm_impressions_cleanup(audio_text)
    print("updated_text", updated_text)

    return {"audio_text": audio_text}


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    manager = ConnectionManager()

    try:
        await manager.connect(websocket, client_id)

        async with aiofiles.open(manager.recording_files[client_id], "wb") as out_file:
            while True:
                # Receive message and detect its type
                message = await websocket.receive()

                if message.get("text") == "reset_recording":
                    # TODO: copy file with timestamp as original to settings.MEDIA_AWS_DIR_PATH

                    # Reset the file pointer to prevent append to file
                    await out_file.seek(0)
                    await out_file.truncate(0)
                else:
                    await out_file.write(message.get("bytes"))
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        await websocket.close(code=1000, reason="Server error")
