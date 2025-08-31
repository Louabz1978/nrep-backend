from pydantic import BaseModel

class AreaCreate(BaseModel):
    title: str
    county: int

    model_config = {
        "from_attributes": True
    }
    