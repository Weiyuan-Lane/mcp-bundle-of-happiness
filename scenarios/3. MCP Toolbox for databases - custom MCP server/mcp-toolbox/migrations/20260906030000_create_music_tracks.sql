CREATE TABLE music_tracks (
  id VARCHAR(255) PRIMARY KEY,
  genre_id VARCHAR(255) REFERENCES genres(id),
  tempo INTEGER NOT NULL CHECK (tempo >= 0)
);
CREATE INDEX idx_music_tracks_genre_id_tempo ON music_tracks (genre_id, tempo);
