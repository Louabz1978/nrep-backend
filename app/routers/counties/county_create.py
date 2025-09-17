from pydantic import BaseModel

class CountyCreate(BaseModel):
    title: str

    model_config = {
        "from_attributes": True
    }
    