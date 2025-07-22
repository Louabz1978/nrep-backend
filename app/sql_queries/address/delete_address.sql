UPDATE users SET address_id = NULL WHERE address_id = :address_id;
DELETE FROM addresses WHERE address_id = :address_id;