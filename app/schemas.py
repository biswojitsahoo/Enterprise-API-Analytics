from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["admin", "analyst", "viewer"]
RecordStatus = Literal["open", "in_progress", "closed"]
Priority = Literal["low", "medium", "high", "critical"]


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=10, max_length=128)
    role: Role = "viewer"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecordCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: RecordStatus = "open"
    priority: Priority = "medium"
    owner: str = Field(min_length=2, max_length=120)


class RecordUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: RecordStatus | None = None
    priority: Priority | None = None
    owner: str | None = Field(default=None, min_length=2, max_length=120)


class RecordRead(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    owner: str
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecordPage(BaseModel):
    items: list[RecordRead]
    total: int
    page: int
    page_size: int
    pages: int


class StatusCount(BaseModel):
    status: str
    count: int


class MonthlyCount(BaseModel):
    month: str
    count: int


class AnalyticsOverview(BaseModel):
    total_records: int
    open_records: int
    in_progress_records: int
    closed_records: int
    high_priority_records: int
