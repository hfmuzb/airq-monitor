import enum
import uuid

from sqlalchemy import Column, String, Enum, func, DateTime
from sqlalchemy.dialects.postgresql import UUID

from db.models.base import Base


class RoleChoices(enum.Enum):
    admin = 1
    maintainer = 2
    user = 3


class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, server_onupdate=func.now())
    deleted_at = Column(DateTime)

    username = Column(String, nullable=False)
    email = Column(String, nullable=False, default='default@default.com')
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleChoices), nullable=False, default=RoleChoices.user)
