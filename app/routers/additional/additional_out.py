from pydantic import BaseModel
from typing import Optional

class AdditionalOut(BaseModel):
    elevator: Optional[ bool ]
    balcony: Optional[ int ]
    ac: Optional[ bool ]
    fan_number: Optional[ int ]
    garage: Optional[ bool ]
    garden: Optional[ bool ]
    solar_system: Optional[ bool ]
    water: Optional[ str ]
    jacuzzi: Optional[ bool ]
    pool: Optional[ bool ]

    model_config = {
        "from_attributes": True
    }
    