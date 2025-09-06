import enum

class PropertyStatus(enum.Enum):
    active = (1, "active")
    pending = (2, "pending")
    closed = (3, "closed")
    out_of_market = (4, "out of market")

    def __init__(self, id: int, label: str):
        self.id = id
        self.label = label

    def as_dict(self):
        return {"id": self.id, "label": self.label}
