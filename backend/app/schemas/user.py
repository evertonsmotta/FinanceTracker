from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
