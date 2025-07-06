from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    buyer = "buyer"
    seller = "seller"
    broker = "broker"
    realtor = "realtor"

    model_config = {
        "from_attributes": True
    }
