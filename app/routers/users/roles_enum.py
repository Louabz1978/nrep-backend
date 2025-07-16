from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    buyer = "buyer"
    seller = "seller"
    broker = "broker"
    realtor = "realtor"
    tenant = "tenant"

    model_config = {
        "from_attributes": True
    }
