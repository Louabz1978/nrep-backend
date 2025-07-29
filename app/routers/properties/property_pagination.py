from pydantic import BaseModel
from .property_out import PropertyOut

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedProperties(BaseModel):
    data: list[PropertyOut]
    pagination: PaginationMeta
