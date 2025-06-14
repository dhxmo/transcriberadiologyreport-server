from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from ..config import settings, DBOption

if settings.DB_ENGINE == DBOption.SQLITE:
    DATABASE_URI = settings.SQLITE_URI
    DATABASE_PREFIX = settings.SQLITE_ASYNC_PREFIX
    DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"
if settings.DB_ENGINE == DBOption.POSTGRES:
    DATABASE_URI = settings.POSTGRES_URI
    DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
    DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)

local_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def async_get_db() -> AsyncSession:
    async_session = local_session
    async with async_session() as db:
        yield db
