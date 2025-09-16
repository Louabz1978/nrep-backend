from ..routers.users.user_out import UserOut
from typing import Optional

from ..routers.agencies.agency_out import AgencyOut

def build_user_out(row: dict, prefix: str) -> Optional[UserOut]:
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
