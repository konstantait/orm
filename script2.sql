SELECT
	t.Name, MAX(t.Bytes)
FROM
	tracks t
WHERE
	t.Milliseconds > 200
	