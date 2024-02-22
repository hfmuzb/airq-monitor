from uuid import UUID
from datetime import datetime
from typing import Optional

from schemas.base import BaseSchema, BasePaginatedSchema


class DeviceSchema(BaseSchema):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    lat: Optional[float] = None
    long: Optional[float] = None

    sensor_type: Optional[str] = None
    name: Optional[str] = None
    uid: str


class PaginatedDeviceListSchema(BasePaginatedSchema[DeviceSchema]): ...


class DeviceCreateSchema(BaseSchema):
    lat: Optional[float] = None
    long: Optional[float] = None
    name: Optional[str] = None
    sensor_type: Optional[str] = None
    uid: str


class DevicePartialUpdateSchema(DeviceCreateSchema):
    uid: Optional[str] = None
