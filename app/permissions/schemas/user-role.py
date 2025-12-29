from pydantic import BaseModel


class AssignRole(BaseModel):
    role_id: int
