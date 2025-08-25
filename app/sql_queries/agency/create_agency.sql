INSERT INTO AGENCIES (
    name,
    email,
    phone_number,
    broker_id,
    created_at,
    created_by
)
VALUES(
    :name,
    :email,
    :phone_number,
    :broker_id,
    :created_at,
    :created_by
)
RETURNING agency_id;