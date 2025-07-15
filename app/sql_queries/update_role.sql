UPDATE roles
SET admin = :admin,
    broker = :broker,
    realtor = :realtor,
    seller = :seller,
    buyer = :buyer,
    tenant = :tenant
WHERE roles_id = (
    SELECT role_id
    FROM users
    WHERE user_id = :user_id
);
