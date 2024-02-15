from pydantic import BaseModel


class MeasurementBase(BaseModel):
    data: str
