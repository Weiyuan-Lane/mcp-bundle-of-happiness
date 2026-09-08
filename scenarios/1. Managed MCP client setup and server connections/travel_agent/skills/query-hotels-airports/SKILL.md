---
name: query-hotels-airports
description: Query the hotels and airports tables with execute_sql. Use when the user asks about hotels, airports, lodging, IATA or ICAO codes, star ratings, or airport/hotel locations in a city or country.
---

Load the matching schema from assets before writing SQL, then call execute_sql.

- Hotels: load `assets/hotels.sql`
- Airports: load `assets/airports.sql`
- For names, use LIKE to search.
- Do not call Google Maps for hotels or airports unless SQL returns no matching rows.
