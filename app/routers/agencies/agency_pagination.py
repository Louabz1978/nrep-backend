from pydantic import BaseModel
from .agency_out import AgencyOut   
from ...utils.pagination import PaginationMeta

class PaginatedAgencyOut(BaseModel):
    data: list[AgencyOut]
    pagination: PaginationMeta
