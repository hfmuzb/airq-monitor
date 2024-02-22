from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from schemas.base import BaseSchema, BasePaginatedSchema


class MeasurementEncodedPayload(BaseModel):
    data: str


class MeasurementDecodedSchema(BaseSchema):
    device_id: str
    sensor_type: str | None = None
    pm1: float | None = None
    pm2_5: float | None = None
    pm10: float | None = None
    time: datetime | None = None


class MeasurementItemSchema(BaseSchema):
    id: UUID
    device_id: UUID
    pm1: float | None = None
    pm2_5: float | None = None
    pm10: float | None = None
    time_: datetime | None = None


class PaginatedMeasurementListSchema(BasePaginatedSchema[MeasurementItemSchema]): ...


class MeasurementCreateSchema(BaseSchema):
    time_: datetime | None = None
    pm1: float | None = None
    pm2_5: float | None = None
    pm10: float | None = None
    device_id: UUID


class MeasurementPartialUpdateSchema(MeasurementCreateSchema):
    device_id: UUID | None = None
