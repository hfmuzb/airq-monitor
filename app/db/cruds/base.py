import abc
import logging
from typing import Generic, TypeVar, Type, Callable, Optional, Sequence, Tuple
from fastapi import HTTPException

from sqlalchemy import Select, Update, Delete, ColumnClause, Result, Row
from sqlalchemy import func, column, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.future import select
from sqlalchemy.orm import InstrumentedAttribute
from core.config import settings, EnvironmentEnum
from db.models.base import Base as BaseDbModel
from schemas.base import BaseSchema, BasePaginatedSchema

IN_SCHEMA = TypeVar("IN_SCHEMA", bound=BaseSchema)
OUT_SCHEMA = TypeVar("OUT_SCHEMA", bound=BaseSchema)
PARTIAL_UPDATE_SCHEMA = TypeVar("PARTIAL_UPDATE_SCHEMA", bound=BaseSchema)
PAGINATED_SCHEMA = TypeVar("PAGINATED_SCHEMA", bound=BasePaginatedSchema)
PAGINATED_LIST_ITEM_SCHEMA = TypeVar(
    "PAGINATED_LIST_ITEM_SCHEMA", bound=BasePaginatedSchema
)
TABLE = TypeVar("TABLE", bound=BaseDbModel)


logger = logging.getLogger(__name__)


class BaseCrud(
    Generic[
        IN_SCHEMA,
        PARTIAL_UPDATE_SCHEMA,
        OUT_SCHEMA,
        PAGINATED_SCHEMA,
        PAGINATED_LIST_ITEM_SCHEMA,
        TABLE,
    ],
    metaclass=abc.ABCMeta,
):
    def __init__(self, db_session: AsyncSession, *args, **kwargs) -> None:
        self._db_session: AsyncSession = db_session

    async def commit_session(self):
        """
        Commits the session if not in testing environment
        :return: None
        """
        if settings.ENVIRONMENT == EnvironmentEnum.DEVELOP:
            await self._db_session.flush()
            return

        await self._db_session.commit()

    async def rollback_session(self):
        """
        Rolls back the session.
        """
        await self._db_session.rollback()

    def apply_active_statement(
        self, stmt: Select | Update | Delete, active_only: bool
    ) -> Select | Update | Delete:
        if active_only:
            return stmt.where(self._table.deleted_at.is_(None))
        return stmt

    @property
    @abc.abstractmethod
    def _table(self) -> Type[TABLE]: ...

    @property
    @abc.abstractmethod
    def _out_schema(self) -> Type[OUT_SCHEMA]: ...

    @property
    @abc.abstractmethod
    def default_ordering(self) -> InstrumentedAttribute: ...

    @property
    @abc.abstractmethod
    def _paginated_schema(self) -> Type[PAGINATED_SCHEMA]: ...

    @property
    @abc.abstractmethod
    def _paginated_list_item_schema(self) -> Type[PAGINATED_LIST_ITEM_SCHEMA]: ...

    @property
    def out_schema_columns(self) -> list[ColumnClause]:
        return [column(i) for i in self._out_schema.model_fields.keys()]

    @property
    def paginated_list_item_schema_columns(self) -> list[ColumnClause]:
        return [
            getattr(self._table, i)
            for i in self._paginated_list_item_schema.model_fields.keys()
        ]

    async def create(
        self, in_schema: IN_SCHEMA, additional_data: dict[str, any] = None
    ) -> OUT_SCHEMA:
        in_data = in_schema.model_dump()
        if additional_data is not None:
            in_data.update(**additional_data)
        entry = self._table(**in_data)
        self._db_session.add(entry)
        await self._db_session.flush()
        return self._out_schema.model_validate(entry)

    async def get_by_id(
        self, entry_id, active_only=True, filter_statement=None
    ) -> OUT_SCHEMA:
        stmt = self.apply_active_statement(
            select(*self.out_schema_columns)
            .select_from(self._table)
            .where(self._table.id == entry_id),
            active_only,
        )
        if filter_statement is not None:
            stmt = stmt.where(filter_statement)
        result = await self._db_session.execute(stmt)
        entry = result.first()
        if not entry:
            raise HTTPException(status_code=404, detail="Object not found")
        return self._out_schema.model_validate(entry)

    async def update_by_id(
        self,
        entry_id,
        in_data: PARTIAL_UPDATE_SCHEMA,
        active_only=True,
        raise_404=True,
        filter_statement=None,
    ) -> None:
        stmt = self.apply_active_statement(
            update(self._table).where(self._table.id == entry_id), active_only
        ).values(**in_data.model_dump(exclude_unset=True))

        if filter_statement is not None:
            stmt = stmt.where(filter_statement)
        result = await self._db_session.execute(stmt)
        if result.rowcount == 0 and raise_404:
            raise HTTPException(status_code=404, detail="Object not found")
        await self._db_session.flush()
        return

    async def delete_by_id(
        self, entry_id, permanently=False, raise_404=True, filter_statement=None
    ) -> None:
        stmt = delete(self._table).where(self._table.id == entry_id)
        if not permanently:
            stmt = self.apply_active_statement(
                update(self._table).where(self._table.id == entry_id), True
            ).values(deleted_at=func.current_timestamp())

        if filter_statement is not None:
            stmt = stmt.where(filter_statement)

        result = await self._db_session.execute(stmt)
        if result.rowcount == 0 and raise_404:  # noqa
            raise HTTPException(status_code=404, detail="Object not found")

        await self._db_session.flush()
        return

    async def get_paginated_list(
        self,
        *,
        limit: int,
        offset: int,
        order_by: UnaryExpression = None,
        active_only=True,
        filter_statement=None,
        join_fn: Optional[Callable[[Select], Select]] = None,
        custom_select_statement: Optional[Select] = None,
        return_raw_result: bool = False,
    ) -> PAGINATED_SCHEMA | Tuple[int, Sequence[Row]]:
        if order_by is None:
            order_by = self.default_ordering

        if custom_select_statement is not None:
            select_stmt = custom_select_statement
        else:
            select_stmt = self.apply_active_statement(
                select(*self.paginated_list_item_schema_columns).select_from(
                    self._table
                ),
                active_only,
            )

        count_stmt = self.apply_active_statement(
            select(func.count()).select_from(self._table), active_only
        )

        if join_fn is not None:
            select_stmt = join_fn(select_stmt)
            count_stmt = join_fn(count_stmt)

        select_stmt = select_stmt.order_by(order_by).limit(limit).offset(offset)
        if filter_statement is not None:
            select_stmt = select_stmt.where(filter_statement)
            count_stmt = count_stmt.where(filter_statement)

        total_count: Result = await self._db_session.execute(count_stmt)
        total_count: int = total_count.scalar()

        if total_count > 0:
            result: Result = await self._db_session.execute(select_stmt)
            entries = result.all()
        else:
            entries = []

        if return_raw_result:
            return total_count, entries

        return self._paginated_schema(
            total=total_count,
            items=[
                self._paginated_list_item_schema.model_validate(entry)
                for entry in entries
            ],
        )
