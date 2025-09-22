from pydantic import BaseModel
from .city_out import CityOut
from ...utils.pagination import PaginationMeta

class PaginatedCities(BaseModel):
    data: list[CityOut]
    pagination: PaginationMeta
