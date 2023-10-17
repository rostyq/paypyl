from pydantic import BaseModel, Field
from .types import UpdateOp


class Update(BaseModel):
    op: UpdateOp
    path: str
    value: str | None = None
    ref: str | None = Field(None, validation_alias="from", serialization_alias="from")

    @classmethod
    def add(cls, path: str, /, value: str) -> "Update":
        return cls(op="add", path=path, value=value)

    @classmethod
    def remove(cls, path: str, /) -> "Update":
        return cls(op="remove", path=path)

    @classmethod
    def replace(cls, path: str, /, value: str) -> "Update":
        return cls(op="replace", path=path, value=value)
