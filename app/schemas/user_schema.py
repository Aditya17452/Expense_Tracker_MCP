from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserOut(BaseModel):
    """Response model — the password hash is never returned."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
