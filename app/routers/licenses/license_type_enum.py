import enum

class LicenseType(enum.Enum):
    individual = (1, "individual", "فردي")
    company = (2, "company", "شركة")

    def __init__(self, id, en, ar):
        self.id = id
        self.en = en
        self.ar = ar

    def as_dict(self):
        return {"id": self.id, "English": self.en, "Arabic": self.ar}
    
    @classmethod
    def validate_dict(cls, value):
        if not isinstance(value, dict):
            raise ValueError("type must be a dictionary")
        required_keys = {"id", "English", "Arabic"}
        if not required_keys.issubset(value.keys()):
            raise ValueError(f"type must contain keys:{required_keys}")
        
        for type_ in cls:
            if( type_.id == value["id"]
                and type_.en == value["English"]
                and type_.ar == value["Arabic"] ):
                return
        raise ValueError(
            f"Invalid combination: {value}. "
            f"Allowed values: {[t.as_dict() for t in cls]}"
        )