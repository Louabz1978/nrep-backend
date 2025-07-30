WITH inserted_user AS (
    INSERT INTO users (
        first_name,
        last_name,
        email,
        password_hash,
        phone_number,
        created_by
    )
    VALUES (
        :first_name,
        :last_name,
        :email,
        :password_hash,
        :phone_number,
        :created_by
    )
    RETURNING user_id
)
INSERT INTO roles ( 
    user_id,
    {role_columns}
)
SELECT
    user_id,
    {role_placeholders}
FROM inserted_user
RETURNING roles_id;
