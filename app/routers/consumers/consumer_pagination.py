from pydantic import BaseModel
from .consumer_out import ConsumerOut

class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedConsumer(BaseModel):
    data: list[ConsumerOut]
    pagination: PaginationMeta
