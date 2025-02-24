from fastapi import APIRouter

from .tasks import router as tasks_router
from .users import router as users_router
from .ws import router as ws_router

router = APIRouter(prefix="/v1")
router.include_router(users_router)
router.include_router(tasks_router)
router.include_router(ws_router)
