from pydantic import BaseModel, model_validator, field_validator
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
    
    @model_validator(mode = "after")
    def validate_values(self):

        errors = []

        if self.balcony is not None and self.balcony < 0:
            raise ValueError("balcony count cannot be negative.")
        
        if self.ac is not None and self.ac < 0:
            raise ValueError("Air conditioner count cannot be negative.")
        
        if self.fan_number is not None and self.fan_number < 0:
            raise ValueError("fan count cannot be negative.")
        
        if self.pool and not self.garden:
            raise ValueError("pool requires a garden.")


        return self

