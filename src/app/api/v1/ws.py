import aiofiles
from starlette.websockets import WebSocketDisconnect
from fastapi import APIRouter, Request, WebSocket, HTTPException

from ...core.ws_connection_manager import ConnectionManager

router = APIRouter(tags=["ws"])


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
