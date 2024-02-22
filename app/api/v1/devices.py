from jose import jwt, JWTError  # noqa
from fastapi import APIRouter, HTTPException, status as http_status
from loguru import logger
from pydantic import ValidationError

from api.dependencies.database import DbSessionDep
from db.cruds.devices import DevicesCrud
from db.cruds.measurements import MeasurementsCrud
from schemas.measurements import (
    MeasurementItemSchema,
    MeasurementCreateSchema,
    MeasurementDecodedSchema,
    MeasurementEncodedPayload,
)
from schemas.devices import DeviceCreateSchema, DeviceSchema
from core.config import settings

router = APIRouter(tags=["Devices"])


@router.post("/measurements", response_model=MeasurementItemSchema)
async def post_measurement(
    measurement: MeasurementEncodedPayload,
    db_session: DbSessionDep,
):
    devices_crud = DevicesCrud(db_session)
    measurements_crud = MeasurementsCrud(db_session)

    data_payload = measurement.data
    try:
        data = MeasurementDecodedSchema.model_validate(
            jwt.decode(
                data_payload,
                settings.DEVICE_DATA_SECRET_KEY,
            )
        )
    except JWTError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not decode JWT",
        )
    except ValidationError as e:
        logger.exception(e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    try:
        device: DeviceSchema = await devices_crud.get_device_by_uid(
            uid=data.device_id,
        )
    except HTTPException as e:
        logger.info(f"Device with id: {data.device_id} not found, creating.")
        device: DeviceSchema = await devices_crud.create(
            DeviceCreateSchema(
                uid=data.device_id,
                sensor_type=data.sensor_type,
            )
        )
        await devices_crud.commit_session()
    measurement_ = await measurements_crud.create(
        in_schema=MeasurementCreateSchema(
            device_id=device.id,
            time_=data.time.replace(tzinfo=None),
            pm2_5=data.pm2_5,
            pm10=data.pm10,
            pm1=data.pm1,
        )
    )
    await measurements_crud.commit_session()
    return measurement_
