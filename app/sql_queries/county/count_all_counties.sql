SELECT count(*) as total
FROM counties
WHERE (:title IS NULL OR title ILIKE :title);