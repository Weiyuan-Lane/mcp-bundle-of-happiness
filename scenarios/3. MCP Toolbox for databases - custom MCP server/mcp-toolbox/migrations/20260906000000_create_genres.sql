CREATE TABLE genres (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);
CREATE INDEX idx_genres_name ON genres (name);
