import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Optional

from pydantic import field_validator, EmailStr
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    name: str = Field(
        ..., min_length=2, max_length=30, schema_extra={"example": "User Userson"}
    )
    email: str = Field(..., schema_extra={"example": "user.userson@example.com"})


class User(UserBase, table=True):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4, primary_key=True)
    hashed_password: str
    is_superuser: bool = Field(default=False)
    tier_id: Optional[int] = Field(default=None, foreign_key="tier.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    is_deleted: bool = Field(default=False)


class UserCreate(UserBase):
    email: EmailStr = Field(
        ...,
        schema_extra={"example": "user@example.com"},
    )
    password: str = Field(
        ...,
        regex="^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        schema_extra={"example": "Str1ngst!"},
    )

    @field_validator("email")
    def validate_email(cls, value: str):
        if "example.com" in value:  # Example additional validation
            raise ValueError("Emails from 'example.com' are not allowed")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserCreateInternal(UserBase):
    hashed_password: str


class UserRead(SQLModel):
    id: int
    name: str
    username: str
    email: str
    tier_id: Optional[int]


class UserUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=2, max_length=30)
    email: Optional[str] = None
    password: str


class UserUpdateInternal(UserUpdate):
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UserTierUpdate(SQLModel):
    tier_id: int


class UserDelete(SQLModel):
    is_deleted: bool
    deleted_at: datetime
