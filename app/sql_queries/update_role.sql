UPDATE roles
SET
    admin = :admin,
    broker = :broker,
    realtor = :realtor,
    seller = :seller,
    buyer = :buyer,
    tenant = :tenant
WHERE roles_id = :role_id;