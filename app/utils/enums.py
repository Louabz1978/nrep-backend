import enum

class PropertyStatus(str, enum.Enum):
    active = "active"
    pending = "pending"
    closed = "closed"
    out_of_market = "out_of_market"

class PropertyTypes(str, enum.Enum):
    apartment = "apartment"
    villa = "villa"
    farm = "farm"
    store = "store"
    land = "land"
    building = "building"

class PropertyTransactionType(str, enum.Enum):
    sell = "sell"
    rent = "rent"

class LicenseType (str, enum.Enum):
    individual = "individual"
    company = "company"

class LicenseStatus (str, enum.Enum):
    active = "active"
    pending = "pending"
    revoked = "revoked"
    canceled = "canceled"
