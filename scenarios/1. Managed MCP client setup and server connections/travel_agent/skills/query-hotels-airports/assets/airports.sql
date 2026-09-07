CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    iata_code CHAR(3) UNIQUE,
    icao_code CHAR(4) UNIQUE,
    city TEXT,
    country_code CHAR(2) NOT NULL,
    timezone TEXT,
    airport_type TEXT NOT NULL DEFAULT 'international',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
