SELECT COUNT(*) As total
FROM cities
WHERE (:title IS NULL OR title ILIKE :title);
