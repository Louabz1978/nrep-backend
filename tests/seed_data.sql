-- Insert admin test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (1, 'admin', 'test', 'test@admin.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 1);

INSERT INTO roles(roles_id, admin, user_id)
VALUES (1, TRUE, 1);

-- Insert broker test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (2, 'broker', 'test', 'test@broker.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 1);

INSERT INTO roles(roles_id, broker, user_id)
VALUES (2, TRUE, 2);

-- Insert realtor test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (3, 'realtor', 'test', 'test@realtor.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 1);

INSERT INTO roles(roles_id, realtor, user_id)
VALUES (3, TRUE, 3);
