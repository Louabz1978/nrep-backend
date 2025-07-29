import enum

class PropertyStatus(str, enum.Enum):
    active = "active"
    pending = "pending"
    closed = "closed"
    out_of_market = "out of market"