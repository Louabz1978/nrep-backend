from pydantic import BaseModel
from .address_out2 import AddressOut2
from ...utils.pagination import PaginationMeta

class PaginatedAddresses(BaseModel):
    data: list[AddressOut2]
    pagination: PaginationMeta