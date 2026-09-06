CREATE TYPE camera_position_type AS ENUM ('front', 'back', 'side', 'moving');
CREATE TABLE camera_positions (
  id VARCHAR(255) PRIMARY KEY,
  description VARCHAR(255) NOT NULL,
  type camera_position_type NOT NULL
);
CREATE INDEX idx_camera_positions_type ON camera_positions (type);
