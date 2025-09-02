INSERT INTO
    licenses (lic_num, lic_status, lic_type, user_id, agency_id)
VALUES
    (:lic_num, :lic_status, :lic_type, :user_id, :agency_id)
    
RETURNING license_id;
