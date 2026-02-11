from app.core.constants.system_roles import SYSTEM_ROLES
from app.core.unit_of_work import UnitOfWork
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_repo import RolePermissionRepository
from app.rbac.repositories.role_repo import RoleRepository


async def seed_roles(uow: UnitOfWork) -> None:
    async with uow as session:
        role_repo = RoleRepository(session)
        perm_repo = PermissionRepository(session)
        rp_repo = RolePermissionRepository(session)

        for role_name, permission_codes in SYSTEM_ROLES.items():
            role = await role_repo.get_or_create(
                name=role_name,
                is_system=True,
            )

            for code in permission_codes:
                perm = await perm_repo.get_by_code(code)
                if not perm:
                    continue

                await rp_repo.assign(role, perm)
