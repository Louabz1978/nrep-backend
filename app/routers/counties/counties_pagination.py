from pydantic import BaseModel
from .county_out import CountyOut
from ...utils.pagination import PaginationMeta

class PaginatedCounties(BaseModel):
    data: list[CountyOut]
    pagination: PaginationMeta