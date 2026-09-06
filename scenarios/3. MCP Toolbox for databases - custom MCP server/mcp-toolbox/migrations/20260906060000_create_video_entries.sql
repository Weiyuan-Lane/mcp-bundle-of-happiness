CREATE TABLE video_entries (
  id serial PRIMARY KEY,
  genre_id VARCHAR(255) REFERENCES genres(id) NULL,
  filming_situation_id VARCHAR(255) REFERENCES filming_situations(id) NULL,
  camera_position_id VARCHAR(255) REFERENCES camera_positions(id) NULL,
  music_track_id VARCHAR(255) REFERENCES music_tracks(id) NULL,
  choreography_id VARCHAR(255) NULL,
  dancer_ids VARCHAR(255)[] NOT NULL DEFAULT '{}'::VARCHAR(255)[],
  video_url VARCHAR(255) NOT NULL
);
