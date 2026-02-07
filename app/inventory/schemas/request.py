from pydantic import BaseModel, Field, model_validator


class CreateProductIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sku: str = Field(min_length=3, max_length=50)


class UpdateProductIn(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    sku: str | None = Field(default=None, min_length=3, max_length=50)

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        if self.name is None and self.sku is None:
            raise ValueError("At least one field must be provided")
        return self
