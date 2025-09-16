INSERT INTO rents (
    property_id,
    sold_price,
    buyer_agent_commission,
    seller_agent_commission,
    date,
    buyer_id,
    seller_id,
    closed_by_id
)
VALUES (
    :property_id,
    :sold_price,
    :buyer_agent_commission,
    :seller_agent_commission,
    :date,
    :buyer_id,
    :seller_id,
    :closed_by_id
)
RETURNING id, property_id, sold_price, date, buyer_id, seller_id, closed_by_id;