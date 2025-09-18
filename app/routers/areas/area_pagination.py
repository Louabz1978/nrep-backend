from pydantic import BaseModel
from .area_out import AreaOut
from ...utils.pagination import PaginationMeta

class PaginatedAreas(BaseModel):
    data: list[AreaOut]
    pagination: PaginationMeta
