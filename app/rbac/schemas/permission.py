from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    id: int
    code: str = Field(..., max_length=100)
    description: str | None = None

    class Config:
        from_attributes = True
