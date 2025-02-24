from datetime import datetime

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class TokenBlacklist(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    token: str = Field(index=True, nullable=False, unique=True)
    expires_at: datetime = Field(nullable=False)


class TokenBlacklistBase(BaseModel):
    token: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    pass

class TokenBlacklistCreateInternal(TokenBlacklistBase):
    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass

class TokenBlacklistUpdateInternal(TokenBlacklistBase):
    pass
