SELECT COUNT(*) As total
FROM areas 
WHERE (:title IS NULL OR title ILIKE :title)
