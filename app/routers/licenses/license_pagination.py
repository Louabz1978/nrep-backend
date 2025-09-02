from pydantic import BaseModel
from .licenses_out import LicenseOut
from ...utils.pagination import PaginationMeta

class PaginatedLicenses(BaseModel):
    data: list[LicenseOut]
    pagination: PaginationMeta
