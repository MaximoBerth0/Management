"""
RBAC seed script.

This module initializes the base RBAC data:
- system permissions
- system roles
- role-permission assignments

It is intended to be executed:
- during application bootstrap
- after database migrations
- in new environments or tests

This file is NOT part of runtime business logic and
should NOT be used inside request handlers.
"""


from app.core.unit_of_work import UnitOfWork
from app.core.constants import SYSTEM_PERMISSIONS, SYSTEM_ROLES
from app.rbac.models import Permission
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_permission_repo import RolePermissionRepository
from app.rbac.repositories.role_repo import RoleRepository


async def seed_permissions(uow: UnitOfWork) -> None:
    async with uow as session:
        perm_repo = PermissionRepository(session)

        for code in SYSTEM_PERMISSIONS:
            existing = await perm_repo.get_by_name(code)
            if not existing:
                await perm_repo.create(
                    Permission(code=code, name=code)
                )

async def seed_roles(uow: UnitOfWork) -> None:
    async with uow as session:
        role_repo = RoleRepository(session)
        perm_repo = PermissionRepository(session)
        rp_repo = RolePermissionRepository(session)

        for role_name, perm_names in SYSTEM_ROLES.items():
            role = await role_repo.get_or_create(role_name)

            for perm_name in perm_names:
                perm = await perm_repo.get_by_name(perm_name)
                if not perm:
                    continue

                await rp_repo.assign(role, perm)


async def seed_all(uow: UnitOfWork) -> None:
    async with uow:
        await seed_permissions(uow)
        await seed_roles(uow)


