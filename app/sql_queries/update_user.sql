UPDATE users
SET
    first_name = :first_name,
    last_name = :last_name,
    email = :email,
    password_hash = :password_hash,
    role = :role,
    phone_number = :phone_number,
    address = :address,

WHERE user_id = :user_id;