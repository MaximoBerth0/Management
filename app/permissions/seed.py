from sqlalchemy.orm import Session

from app.permissions.constants import SYSTEM_PERMISSIONS, SYSTEM_ROLES
from app.permissions.models import Permission
from app.permissions.repositories.permission_repo import PermissionRepository
from app.permissions.repositories.role_permission_repo import RolePermissionRepository
from app.permissions.repositories.role_repo import RoleRepository


def seed_permissions(db: Session):
    perm_repo = PermissionRepository(db)

    for name in SYSTEM_PERMISSIONS:
        if not perm_repo.get_by_name(name):
            perm_repo.create(Permission(name=name))

    db.commit()

def seed_roles(db: Session):
    role_repo = RoleRepository(db)
    perm_repo = PermissionRepository(db)
    rp_repo = RolePermissionRepository(db)

    for role_name, perm_names in SYSTEM_ROLES.items():
        role = role_repo.get_or_creat(role_name)

        for perm_name in perm_names:
            perm = perm_repo.get_by_name(perm_name)
            if not perm:
                continue  

            rp_repo.assign(role, perm)
    db.commit()

def seed_all(db: Session):
    seed_permissions(db)
    seed_roles(db)

