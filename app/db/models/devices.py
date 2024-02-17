from typing import Optional
import uuid

from sqlalchemy import Column, String, func, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID

from db.models.base import Base


class Devices(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, server_onupdate=func.now())
    deleted_at = Column(DateTime)

    lat = Column(DECIMAL, nullable=True, server_default=None)
    long = Column(DECIMAL, nullable=True, server_default=None)
    name = Column(String, nullable=True, server_default=None)
    uid = Column(String, nullable=False, unique=True)


class Measurements(Base):
    __tablename__ = "measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, server_onupdate=func.now())
    deleted_at = Column(DateTime)

    pm1 = Column(DECIMAL, nullable=True, server_default=None)
    pm2_5 = Column(DECIMAL, nullable=True, server_default=None)
    pm10 = Column(DECIMAL, nullable=True, server_default=None)

    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    device: Mapped[Optional["Devices"]] = relationship()
