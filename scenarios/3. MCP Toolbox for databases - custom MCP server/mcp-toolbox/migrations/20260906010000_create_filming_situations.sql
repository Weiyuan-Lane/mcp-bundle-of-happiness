CREATE TABLE filming_situations (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);
CREATE INDEX idx_filming_situations_name ON filming_situations (name);
