from pydantic import BaseModel

class CityCreate(BaseModel):
    title: str

    model_config = {
        "from_attributes": True
    }
    