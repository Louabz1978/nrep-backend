from pydantic import BaseModel
from .property_out import PropertyOut
from ...utils.pagination import PaginationMeta

class PaginatedProperties(BaseModel):
    data: list[PropertyOut]
    pagination: PaginationMeta
