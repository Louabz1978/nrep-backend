UPDATE users
SET
    first_name = COALESCE(:first_name, first_name),
    last_name = COALESCE(:last_name, last_name),
    email = COALESCE(:email, email),
    password_hash = COALESCE(:password_hash, password_hash),
    phone_number = COALESCE(:phone_number, phone_number)
WHERE user_id = :user_id;
