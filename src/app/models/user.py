import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    user_id: str = Field(
        ..., min_length=2, max_length=30, schema_extra={"example": "User Userson"}
    )
    email: str = Field(..., schema_extra={"example": "user.userson@example.com"})


class User(UserBase, table=True):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    tier: Optional[str] = Field(..., schema_extra={"example": "free"})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(UserBase):
    email: str
    tier: str


class UserCreateInternal(UserBase):
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UserRead(SQLModel):
    id: int
    user_id: str
    email: str
    tier: Optional[str]


class UserUpdate(SQLModel):
    tier: Optional[str]


class UserUpdateInternal(UserUpdate):
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
