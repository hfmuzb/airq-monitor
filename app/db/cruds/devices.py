from typing import Type  # noqa

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.sql.elements import UnaryExpression
from db.cruds.base import BaseCrud
from db.models.devices import Devices as DevicesTable
from schemas.devices import (
    DeviceSchema,
    PaginatedDeviceListSchema,
    DevicePartialUpdateSchema,
    DeviceCreateSchema,
)


class DevicesCrud(
    BaseCrud[
        DeviceCreateSchema,  # in_schema
        DevicePartialUpdateSchema,
        DeviceSchema,  # out_schema
        PaginatedDeviceListSchema,
        DeviceSchema,
        DevicesTable,
    ]
):
    @property
    def _table(self) -> Type[DevicesTable]:
        return DevicesTable

    @property
    def _out_schema(self) -> Type[DeviceSchema]:
        return DeviceSchema

    @property
    def default_ordering(self) -> UnaryExpression:
        return DevicesTable.created_at.desc()

    @property
    def _paginated_schema(self) -> Type[PaginatedDeviceListSchema]:
        return PaginatedDeviceListSchema

    @property
    def _paginated_list_item_schema(self) -> Type[DeviceSchema]:
        return DeviceSchema

    async def get_device_by_uid(
        self,
        uid,
        active_only=True,
    ) -> DeviceSchema:
        stmt = self.apply_active_statement(
            select(*self.out_schema_columns)
            .select_from(self._table)
            .where(self._table.uid == uid),
            active_only,
        )
        result = await self._db_session.execute(stmt)
        entry = result.first()
        if not entry:
            raise HTTPException(status_code=404, detail="Object not found")
        return self._out_schema.model_validate(entry)
