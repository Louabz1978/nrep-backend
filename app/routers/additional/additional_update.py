from fastapi import Form
from pydantic import BaseModel
from typing import Optional

class AdditionalUpdate(BaseModel):
    elevator: Optional[ bool| None ] = None
    balcony: Optional[ int ] = None
    ac: Optional[ bool ] = None
    fan_number: Optional[ int ] = None
    garage: Optional[ bool ] = None
    garden: Optional[ bool ] = None
    solar_system: Optional[ bool ] = None
    water: Optional[ str ] = None
    jacuzzi: Optional[ bool ] = None
    pool: Optional[ bool ] = None

    @classmethod
    def as_form(
        cls,
        elevator: Optional[ bool ]= Form(None),
        balcony: Optional[ int ]= Form(None),
        ac: Optional[ bool ]= Form(None),
        fan_number: Optional[ int ]= Form(None),
        garage: Optional[ bool ]= Form(None),
        garden: Optional[ bool ]= Form(None),
        solar_system: Optional[ bool ]= Form(None),
        water: Optional[ str ]= Form(None),
        jacuzzi: Optional[ bool ]= Form(None),
        pool: Optional[ bool ]= Form(None)
    ):
        return cls(
            elevator=elevator,
            balcony=balcony,
            ac=ac,
            fan_number=fan_number,
            garage=garage,
            garden=garden,
            solar_system=solar_system,
            water=water,
            jacuzzi=jacuzzi,
            pool=pool
        )
