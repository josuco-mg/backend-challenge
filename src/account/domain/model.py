from typing import Optional

from pydantic import BaseModel
from pydantic import field_validator


class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: Optional[str] = None
    is_admin: bool = False

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value:
            raise ValueError("Username is required")
        return value
