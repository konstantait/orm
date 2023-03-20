SELECT
	t.Name,
	a.Title 
FROM
	playlist_track pt 
INNER JOIN playlists p USING(PlaylistId)
INNER JOIN tracks t USING(TrackId)
INNER JOIN albums a USING(AlbumId)
WHERE
	p.Name = 'TV Shows'
	