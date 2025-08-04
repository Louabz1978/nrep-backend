import enum

class PropertyTypes(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    house = "house"
    building = "building"
    store = "store"
    farm = "farm"