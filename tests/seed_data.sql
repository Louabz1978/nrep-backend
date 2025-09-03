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

--Insert buyer test account 
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
VALUES (6, 'tenant', 'test', 'test@tenant.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 2);

INSERT INTO roles(roles_id, tenant, user_id)
VALUES (6, TRUE, 6);

INSERT INTO users(user_id, first_name, last_name, email, password_hash, phone_number, created_by)
VALUES (7, 'noRole', 'test', 'test@norole.com', '$2b$12$2h9HK/lHUQxA.YnNt3qKD.XEscVHESnYPp9LodVOHRNsBZO0CHjZG', '0933111222', 1);

INSERT INTO roles(roles_id,user_id)
VALUES (7, 7);


-- Insert address test account
INSERT INTO addresses (floor, apt, area, city, county, building_num, street, created_by)
VALUES (2, 5, 'Downtown', 'Amsterdam', 'Noord-Holland', '12B', 'Main Street', 1);

-- Insert agenct test account
INSERT INTO agencies (agency_id, name, email, phone_number, created_by, broker_id)
VALUES (1, 'test', 'test@test.com', '0959804457', 1, 2);

INSERT INTO agencies (agency_id, name, email, phone_number, created_by, broker_id)
VALUES
    (2, 'Agency A', 'a@test.com', '0959804457', 1, 2),
    (3, 'Agency B', 'b@test.com', '0959804458', 2, 3),
    (4, 'Agency C', 'c@test.com', '0959804459', 1, 2);

INSERT INTO addresses (floor, apt, area, city, county, building_num, street, created_by, agency_id)
VALUES
    (2, 5, 'Downtown', 'Amsterdam', 'Noord-Holland', '12B', 'Main Street', 1, 1),
    (3, 6, 'Uptown', 'Berlin', 'Berlin', '34C', 'Park Ave', 2, 2),
    (1, 4, 'Midtown', 'Paris', 'Paris', '78D', 'Rue St', 1, 3);

--insert new properties 
INSERT INTO properties (
    description,
    show_inst,
    price,
    property_type,
    bedrooms,
    bathrooms,
    property_realtor_commission,
    buyer_realtor_commission,
    area_space,
    year_built,
    latitude,
    longitude,
    status,
    exp_date,
    created_by,
    owner_id,
    images_urls,
    mls_num
) VALUES
(
    'شقة حلوة مع إطلالة على المدينة',
    'اتصل قبل بيوم لعرض العقار',
    150000.00,
    'apartment',
    3,
    2,
    2.5,
    2.0,
    120,
    2015,
    34.7306,
    36.7097,
    'active',
    '2026-01-01',
    1,   -- user_id موجود بجدول users
    2,   -- user_id موجود بجدول users
    null,
    123456
),
(
    'فيلا واسعة مع حديقة وبركة سباحة',
    'مفتوح طول الأسبوع',
    750000.00,
    'villa',
    5,
    4,
    5.0,
    4.5,
    600,
    2020,
    34.7320,
    36.7100,
    'active',
    '2026-05-15',
    2,
    2,
    null,
    789012
);

