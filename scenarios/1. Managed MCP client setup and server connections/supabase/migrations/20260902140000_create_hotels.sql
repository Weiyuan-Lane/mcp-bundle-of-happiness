create table hotels (
  id serial primary key,
  name text not null,
  latitude double precision not null,
  longitude double precision not null,
  address text,
  city text,
  country_code char(2) not null,
  star_rating smallint,
  phone text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
ALTER TABLE public.hotels ENABLE ROW LEVEL SECURITY;

create index hotels_city_idx on hotels (city);
create index hotels_country_code_idx on hotels (country_code);
