from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=200)


class PaginatedResponse(BaseModel):
    items: list
    page: int
    page_size: int
    total: int

