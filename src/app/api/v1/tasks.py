from typing import Any

from arq.jobs import Job as ArqJob
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from ...core.config import settings
from ...core.utils import queue

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/task/{task_id}")
async def get_task(task_id: str) -> dict[str, Any] | None:
    """Get information about a specific background task.

    Parameters
    ----------
    task_id: str
        The ID of the task.

    Returns
    -------
    Optional[dict[str, Any]]
        A dictionary containing information about the task if found, or None otherwise.
    """
    job = ArqJob(task_id, queue.pool)
    job_info: dict = await job.info()
    return vars(job_info)


# {"updated_text": updated_text} for find
#  {"audio_text": audio_text} for impre


class JobResponse(BaseModel):
    id: str


@router.post("/transcribe-findings")
async def transcribe_findings(request: Request):
    try:
        req_body = await request.json()
        audio_file = f"{settings.MEDIA_DIR_PATH}/{str(req_body['audio_uuid'])}.webm"

        job = await queue.pool.enqueue_job("transcribe_findings", req_body, audio_file)

        return {"id": job.job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/transcribe-impression")
async def transcribe_impression(request: Request):
    req_body = await request.json()
    audio_file = f"{settings.MEDIA_DIR_PATH}/{str(req_body['audio_uuid'])}.webm"

    job = await queue.pool.enqueue_job("transcribe_impressions", audio_file)
    return {"id": job.job_id}
