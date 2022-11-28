from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema
from app.schemas.types import StrDict, UnicodeStr


class TypeMeta(BaseSchema):
    api_version: UnicodeStr = Field(..., alias="APIVersion")
    kind: UnicodeStr = Field(..., alias="Kind")


class ObjectMetadata(BaseSchema):
    name: UnicodeStr
    namespace: UnicodeStr = "default"
    uid: UUID
    version: int = Field(default=1, alias="ResourceVersion")
    created_at: datetime = Field(..., alias="CreationTimestamp")
    deleted_at: Optional[datetime] = Field(None, alias="DeletionTimestamp")
    labels: StrDict = {}
    annotations: StrDict = {}


class Status(BaseSchema):
    status: Optional[UnicodeStr] = None
    message: Optional[str] = None
    reason: Optional[str] = None
    code: Optional[int] = None
