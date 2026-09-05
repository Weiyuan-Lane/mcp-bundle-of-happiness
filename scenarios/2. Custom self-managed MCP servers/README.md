# Scenario 2: Custom self-managed MCP servers

← [Back to MCP Bundle of Happiness](../../README.md)

This scenario runs **your own MCP servers** next to the ADK client. The exchange-rate and QuickChart servers are FastMCP apps in Docker. The **financial advisor agent** is the **client**: it connects over Streamable HTTP and calls those tools.

The agent converts any two currencies, looks up current and historical rates, and can chart a series with QuickChart when that helps.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App | Description | URL |
|---------------|-------------|-----|
| **ADK UI** | MCP test client — financial advisor agent below | [http://localhost:8080](http://localhost:8080) |
| **Exchange-rate MCP** | Self-managed FastMCP server for currency rates and conversions | [http://localhost:8091/mcp](http://localhost:8091/mcp) |
| **QuickChart MCP** | Self-managed FastMCP server that returns a QuickChart image URL | [http://localhost:8092/mcp](http://localhost:8092/mcp) |

## Financial advisor agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Connects over Streamable HTTP and lets the model call the tools |
| **Server** | Exchange-rate MCP (self-managed) | Current rates (`get_currency_data`), pairwise conversion (`convert_from_one_currency_to_another_currency`), and historical series (`exchange_rate_time_series_data`) via [Frankfurter](https://www.frankfurter.app/) |
| **Server** | QuickChart MCP (self-managed) | Builds a chart image URL (`make_chart`) from a [QuickChart](https://quickchart.io/)/Chart.js-compatible dict |
