from pydantic import BaseModel

class AreaCreate(BaseModel):
    title: str
    city: int

    model_config = {
        "from_attributes": True
    }
    