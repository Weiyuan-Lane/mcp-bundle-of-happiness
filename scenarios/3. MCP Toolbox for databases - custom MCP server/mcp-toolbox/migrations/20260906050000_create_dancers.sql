CREATE TYPE age_range AS ENUM ('20-25 years old', '25-30 years old', '30-35 years old');
CREATE TYPE gender AS ENUM ('Male', 'Female');
CREATE table dancers (
  id VARCHAR(255) PRIMARY KEY,
  gender gender NOT NULL,
  age_range age_range NOT NULL,
  dance_experience_year FLOAT NOT NULL,
  genre_id VARCHAR(255) REFERENCES genres(id)
);
CREATE INDEX idx_dancers_genre_id_gender_age_range_dance_experience_year ON dancers (genre_id, gender, age_range, dance_experience_year);
