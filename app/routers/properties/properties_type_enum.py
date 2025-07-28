import enum

class PropertyTypes(str, enum.Enum):
    apartment = "Apartment"
    villa = "Villa"
    house = "House"
    building = "Building"
    store = "Store"
    farm = "Farm"