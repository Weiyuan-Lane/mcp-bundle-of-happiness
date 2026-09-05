# Scenario 1: Managed MCP client setup and server connections

← [Back to MCP Bundle of Happiness](../../README.md)

This scenario connects ADK agents to **managed MCP servers** from Google Maps and Supabase. Those servers already exist on the public internet. The agents are the **clients**: they authenticate over Streamable HTTP and call the tools those services expose.

The **DevOps agent** administrates the database, such as for applying `supabase/migrations/` through Supabase MCP. The **travel agent** uses Maps for places, weather, and routes, and can query `hotels` / `airports` in Supabase.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App | Description | URL |
|---------------|-------------|-----|
| **ADK UI** | MCP test client — travel and devops agents below | [http://localhost:8080](http://localhost:8080) |

## DevOps agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Connects over Streamable HTTP and lets the model call the tools |
| **Server** | `@modelcontextprotocol/server-filesystem` | Read-only tools scoped to `supabase/migrations/` |
| **Server** | [Supabase MCP (managed service)](https://supabase.com/docs/guides/ai-tools/mcp) | Database administration with tools - `list_tables`, `list_extensions`, `list_migrations`, `apply_migration`, `execute_sql`. Authorisation is required with the supplied `SCENARIO_1_SUPABASE_TOKEN` env value. |

## Travel agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Connects over Streamable HTTP and lets the model call the tools |
| **Server** | [Google Maps MCP (managed service)](https://developers.google.com/maps/ai/grounding-lite) | Places, weather, and routes ([tool list](https://developers.google.com/maps/ai/grounding-lite#tools)). Authorisation is required with the supplied `SCENARIO_1_GOOGLE_MAPS_API_KEY` env value. |
| **Server** (optional) | [Supabase MCP (managed service)](https://supabase.com/docs/guides/ai-tools/mcp) | Table data access for `hotels` and `airports`. Authorisation is required with the supplied `SCENARIO_1_SUPABASE_TOKEN` env value. |
