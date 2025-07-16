WITH inserted_role AS (
    INSERT INTO roles ({role_columns})
    VALUES ({role_placeholders})
    RETURNING roles_id
)
INSERT INTO USERS (
    first_name,
    last_name,
    email,
    password_hash,
    role_id,
    phone_number,
    created_by
)
VALUES(
    :first_name,
    :last_name,
    :email,
    :password_hash,
    (SELECT roles_id FROM inserted_role),
    :phone_number,
    :created_by
)
RETURNING user_id;