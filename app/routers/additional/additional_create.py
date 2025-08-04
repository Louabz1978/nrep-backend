from pydantic import BaseModel
from typing import Optional
from fastapi import Form

class AdditionalCreate(BaseModel):
    elevator: Optional[ bool| None ] = None
    balcony: Optional[ int ] = None
    ac: Optional[ int ] = None
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
        elevator: Optional[ bool ]= Form(...),
        balcony: Optional[ int ]= Form(...),
        ac: Optional[ int ]= Form(...),
        fan_number: Optional[ int ]= Form(...),
        garage: Optional[ bool ]= Form(...),
        garden: Optional[ bool ]= Form(...),
        solar_system: Optional[ bool ]= Form(...),
        water: Optional[ str ]= Form(...),
        jacuzzi: Optional[ bool ]= Form(...),
        pool: Optional[ bool ]= Form(...)
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
