from ..routers.users.user_out import UserOut
from ..routers.consumers.consumer_out import ConsumerOut

from ..routers.agencies.agency_out import AgencyOut

def build_user_out(row: dict, prefix: str) -> UserOut | None:
    if not row.get(f"{prefix}first_name"):
        return None
    roles = []
    if row.get(f"{prefix}admin"):
        roles.append("admin")
    if row.get(f"{prefix}broker"):
        roles.append("broker")
    if row.get(f"{prefix}realtor"):
        roles.append("realtor")
    if row.get(f"{prefix}buyer"):
        roles.append("buyer")
    if row.get(f"{prefix}seller"):
        roles.append("seller")
    if row.get(f"{prefix}tenant"):
        roles.append("tenant")

    return UserOut(
        user_id=row.get(f"{prefix}user_id"),
        first_name=row.get(f"{prefix}first_name"),
        last_name=row.get(f"{prefix}last_name"),
        email=row.get(f"{prefix}email"),
        phone_number=row.get(f"{prefix}phone_number"),
        roles=roles,
        created_by=row.get(f"{prefix}created_by"),
        created_at=row.get(f"{prefix}created_at")

        # address=row.get(f"{prefix}address"),
        # agency=AgencyOut(
        #     agency_id=row.get(f"{prefix}agency_id"),
        #     name=row.get(f"{prefix}agency_name"),
        #     phone_number=row.get(f"{prefix}agency_phone_number")
        # ) if row.get(f"{prefix}agency_id") else None
    )

def build_consumer_out(row: dict, prefix: str) -> ConsumerOut | None:
    if not row.get(f"{prefix}name"):
        return None
    roles = []
    if row.get(f"{prefix}admin"):
        roles.append("admin")
    if row.get(f"{prefix}broker"):
        roles.append("broker")
    if row.get(f"{prefix}realtor"):
        roles.append("realtor")
    if row.get(f"{prefix}buyer"):
        roles.append("buyer")
    if row.get(f"{prefix}seller"):
        roles.append("seller")
    if row.get(f"{prefix}tenant"):
        roles.append("tenant")

    return ConsumerOut(
        consumer_id=row.get(f"{prefix}consumer_id"),
        name=row.get(f"{prefix}name"),
        father_name=row.get(f"{prefix}father_name"),
        surname=row.get(f"{prefix}surname"),
        mother_name_surname=row.get(f"{prefix}mother_name_surname"),
        place_birth=row.get(f"{prefix}place_birth"),
        date_birth=row.get(f"{prefix}date_birth"),
        registry=row.get(f"{prefix}registry"),
        national_number=row.get(f"{prefix}national_number"),
        email=row.get(f"{prefix}email"),
        phone_number=row.get(f"{prefix}phone_number"),
        roles=roles,
        created_by=row.get(f"{prefix}created_by"),  
        created_at=row.get(f"{prefix}created_at")
    )