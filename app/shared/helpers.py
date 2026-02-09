from app.rbac.models.main_model import Role
from app.shared.exceptions import RoleNotFound


async def _get_role_or_fail(self, role_id: int) -> Role:
    role = await self.role_repo.get_by_id(role_id)
    if not role:
        raise RoleNotFound()
    return role

