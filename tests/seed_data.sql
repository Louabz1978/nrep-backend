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
VALUES (3, 'realtor', 'test', 'test@realtor.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 2);

INSERT INTO roles(roles_id, realtor, user_id)
VALUES (3, TRUE, 3);

-- Insert buyer test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (4, 'buyer', 'test', 'test@buyer.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 3);

INSERT INTO roles(roles_id, buyer, user_id)
VALUES (4, TRUE, 4);

-- Insert seller test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (5, 'seller', 'test', 'test@seller.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 3);

INSERT INTO roles(roles_id, seller, user_id)
VALUES (5, TRUE, 5);

-- Insert tenant test account
INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (6, 'tenant', 'test', 'test@tenant.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 3);

INSERT INTO roles(roles_id, tenant, user_id)
VALUES (6, TRUE, 6);