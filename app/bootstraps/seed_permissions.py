from app.core.constants.inventory_permissions import INVENTORY_PERMISSIONS
from app.core.constants.system_permissions import SYSTEM_PERMISSIONS
from app.core.unit_of_work import UnitOfWork
from app.rbac.models import Permission
from app.rbac.repositories.permission_repo import PermissionRepository

ALL_PERMISSIONS = set(
    SYSTEM_PERMISSIONS + INVENTORY_PERMISSIONS
)


async def seed_permissions(uow: UnitOfWork) -> None:
    async with uow as session:
        repo = PermissionRepository(session)

        for code in ALL_PERMISSIONS:
            existing = await repo.get_by_code(code)
            if existing:
                continue

            await repo.create(
                Permission(
                    code=code,
                    name=code,
                    description=f"Permission: {code}",
                )
            )
