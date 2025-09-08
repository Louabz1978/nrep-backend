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
    images_urls,
    mls_num,
    created_by,
    owner_id
) VALUES 
(
    'Cozy house with small garden',
    'Call for visit',
    120000.00,
    'house',
    3,
    2,
    2.0,
    1.0,
    180,
    2012,
    34.7325,
    36.7131,
    'active',
    '2026-12-31',
    NULL,
    20001,
    1,
    1
),
(
    'Modern apartment with balcony',
    'Email to schedule',
    85000.00,
    'apartment',
    2,
    1,
    1.5,
    1.0,
    95,
    2019,
    34.7300,
    36.7150,
    'available',
    '2026-06-30',
    NULL,
    20002,
    2,
    1
),
(
    'Luxury villa with private pool',
    'By appointment only',
    400000.00,
    'villa',
    5,
    4,
    4.5,
    3.0,
    550,
    2021,
    34.7400,
    36.7200,
    'sold',
    '2027-01-15',
    NULL,
    20003,
    3,
    2
),
(
    'Office space downtown',
    'Call agent',
    100000.00,
    'office',
    0,
    1,
    2.0,
    1.5,
    150,
    2015,
    34.7350,
    36.7100,
    'active',
    '2026-11-30',
    NULL,
    20004,
    1,
    2
),
(
    'Small studio apartment',
    'Available immediately',
    50000.00,
    'apartment',
    1,
    1,
    1.0,
    0.5,
    45,
    2020,
    34.7380,
    36.7180,
    'available',
    '2026-08-20',
    NULL,
    20005,
    2,
    1
);


INSERT INTO consumers 
(name, father_name, surname, mother_name_surname, place_birth, date_birth, registry, national_number, email, phone_number, created_by_type, created_by)
VALUES
('Ahmad', 'Khaled', 'Al-Hamwi', 'Fatima Al-Sayed', 'Homs', '1995-04-12', 'Registry-001', 123456789, 'ahmad@example.com', '+963991234567', 'admin', 1);

INSERT INTO consumers 
(name, father_name, surname, mother_name_surname, place_birth, date_birth, registry, national_number, email, phone_number, created_by_type, created_by)
VALUES
('Sara', 'Omar', 'Al-Khatib', 'Layla Al-Ahmad', 'Damascus', '1998-09-30', 'Registry-002', 987654321, 'sara.khatib@example.com', '+963944556677', 'broker', 2);

INSERT INTO consumers 
(name, father_name, surname, mother_name_surname, place_birth, date_birth, registry, national_number, email, phone_number, created_by_type, created_by)
VALUES
('Hussein', 'Mahmoud', 'Al-Ali', 'Aisha Al-Sheikh', 'Aleppo', '1990-01-05', 'Registry-003', 456789123, 'hussein.ali@example.com', '+963933221144', 'realtor', 3);