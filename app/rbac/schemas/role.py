from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str | None = Field(None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, max_length=255)

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True

