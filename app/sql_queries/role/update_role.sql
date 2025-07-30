UPDATE roles
SET admin = :admin,
    broker = :broker,
    realtor = :realtor,
    seller = :seller,
    buyer = :buyer,
    tenant = :tenant
WHERE user_id = :user_id
