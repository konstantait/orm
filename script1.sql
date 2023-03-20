SELECT
	tracks.Name,
	genres.Name,
	media_types.Name
FROM
	tracks
INNER JOIN media_types USING(MediaTypeId)
INNER JOIN genres USING(GenreId)
WHERE
	media_types.Name = 'AAC audio file'
	AND genres.Name LIKE 'R%'
	