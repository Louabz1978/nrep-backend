from ..routers.users.user_out import UserOut

from ..routers.agencies.agency_out import AgencyOut

def build_user_out(row: dict, prefix: str) -> UserOut | None:
    if not row.get(f"{prefix}first_name"):
        return None

    return UserOut(
        user_id=row.get(f"{prefix}user_id"),
        first_name=row.get(f"{prefix}first_name"),
        last_name=row.get(f"{prefix}last_name"),
        email=row.get(f"{prefix}email"),
        phone_number=row.get(f"{prefix}phone_number"),

        # address=row.get(f"{prefix}address"),
        # agency=AgencyOut(
        #     agency_id=row.get(f"{prefix}agency_id"),
        #     name=row.get(f"{prefix}agency_name"),
        #     phone_number=row.get(f"{prefix}agency_phone_number")
        # ) if row.get(f"{prefix}agency_id") else None
    )
