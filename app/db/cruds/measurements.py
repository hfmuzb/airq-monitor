from typing import Type  # noqa

from sqlalchemy.sql.elements import UnaryExpression
from db.cruds.base import BaseCrud
from db.models.devices import Measurements as MeasurementsTable
from schemas.measurements import (
    MeasurementItemSchema,
    PaginatedMeasurementListSchema,
    MeasurementPartialUpdateSchema,
    MeasurementCreateSchema,
)


class MeasurementsCrud(
    BaseCrud[
        MeasurementCreateSchema,  # in_schema
        MeasurementPartialUpdateSchema,
        MeasurementItemSchema,  # out_schema
        PaginatedMeasurementListSchema,
        MeasurementItemSchema,
        MeasurementsTable,
    ]
):
    @property
    def _table(self) -> Type[MeasurementsTable]:
        return MeasurementsTable

    @property
    def _out_schema(self) -> Type[MeasurementItemSchema]:
        return MeasurementItemSchema

    @property
    def default_ordering(self) -> UnaryExpression:
        return MeasurementsTable.created_at.desc()

    @property
    def _paginated_schema(self) -> Type[PaginatedMeasurementListSchema]:
        return PaginatedMeasurementListSchema

    @property
    def _paginated_list_item_schema(self) -> Type[MeasurementItemSchema]:
        return MeasurementItemSchema
