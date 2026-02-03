from pydantic import BaseModel, Field


class PermissionAssign(BaseModel):
    permission_id: int = Field(..., gt=0)
