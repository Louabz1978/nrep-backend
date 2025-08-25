from pydantic import BaseModel
from .agency_out import AgencyOut

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedAgency(BaseModel):
    data: list[AgencyOut]
    pagination: PaginationMeta
