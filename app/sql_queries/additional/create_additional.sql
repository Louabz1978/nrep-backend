INSERT INTO additional(
    elevator,
    balcony,
    ac,
    fan_number,
    garage,
    garden,
    solar_system,
    water,
    jacuzzi,
    pool,
    property_id
)
VALUES(
    :elevator,
    :balcony,
    :ac,
    :fan_number,
    :garage,
    :garden,
    :solar_system,
    :water,
    :jacuzzi,
    :pool,
    :property_id
)
RETURNING additional_id;