CREATE TABLE choreographies (
  id VARCHAR(255),
  genre_id VARCHAR(255) REFERENCES genres(id),
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (genre_id, id)
);
CREATE INDEX idx_choreographies_genre_id_name ON choreographies (genre_id, name);
