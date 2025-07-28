import enum

class PropertyStatus(str, enum.Enum):
    active = "Active"
    pending = "Pending"
    closed = "Closed"
    out_of_market = "Out of Market"