from pydantic import BaseModel
from .user_out import UserOut

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedUser(BaseModel):
    data: list[UserOut]
    pagination: PaginationMeta
