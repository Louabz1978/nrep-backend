from pydantic import BaseModel

class CountyCreate(BaseModel):
    title: str
    city: int

    model_config = {
        "from_attributes": True
    }
    