from loguru import logger

from fastapi import APIRouter

from api.dependencies.database import DbSessionDep
from schemas.measurement_schemas import MeasurementBase

router = APIRouter(tags=["Devices"])


@router.post("/measurements")
async def post_measurement(
    measurement: MeasurementBase,
    db_session: DbSessionDep,
):
    logger.info(measurement.data)
    return
