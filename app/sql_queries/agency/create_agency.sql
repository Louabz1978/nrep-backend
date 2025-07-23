INSERT INTO AGENCIES (
    name,
    email,
    phone_number,
    address,
    neighborhood,
    city,
    county,
    broker_id
)
VALUES(
    :name,
    :email,
    :phone_number,
    :address,
    :neighborhood,
    :city,
    :county,
    :broker_id
)
RETURNING agency_id;