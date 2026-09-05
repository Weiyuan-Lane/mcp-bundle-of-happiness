create table airports (
  id serial primary key,
  name text not null,
  latitude double precision not null,
  longitude double precision not null,
  iata_code char(3) unique,
  icao_code char(4) unique,
  city text,
  country_code char(2) not null,
  timezone text,
  airport_type text not null default 'international',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
ALTER TABLE public.airports ENABLE ROW LEVEL SECURITY;

create index airports_city_idx on public.airports (city);
create index airports_country_code_idx on public.airports (country_code);
