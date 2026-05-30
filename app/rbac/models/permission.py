from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base
from app.rbac.models.role_permission import role_permissions

if TYPE_CHECKING:
    from app.rbac.models.role import Role

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(250))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )
