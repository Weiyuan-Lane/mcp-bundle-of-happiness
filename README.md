# MCP Bundle of Happiness

I have no idea why I named it as this. :grimacing:

## Setup

Make sure you clone with submodules
```
git clone --recurse-submodules git@github.com:Weiyuan-Lane/mcp-bundle-of-happiness.git
```

ChromeDevTools MCP is used for one of the scenarios, so make sure you use Chrome too
Install Chrome [here](https://www.google.com/chrome/)

Duplicate `.env.sample` to `.env`, and fill in the missing values

Finally, start and stop the all scenarios with make commands (this also opens Chrome with remote debugging for ChromeDevTools MCP):
```
make docker-compose-up          # Start
make docker-compose-down        # Stop
```

## Scenarios

| Scenario | Lesson(s) |
| --- | --- |
| [0. Simple MCP client and server setup](scenarios/0.%20Simple%20MCP%20client%20and%20server%20setup/README.md) | <ul><li><b>Configure a simple filesystem MCP server</b></li><li>Setup a MCP client using an agent built in ADK 2.0</li></ul> |
| [1. Managed MCP client setup and server connections](scenarios/1.%20Managed%20MCP%20client%20setup%20and%20server%20connections/README.md) | <ul><li><b>Connect to managed MCP servers provided by other services (Google Maps, Supabase)</b></li><li>Configure multiple MCP servers within one agent</li><li>Configure an auth token or API key to access an MCP server</li><li>Filter tools per agent so DevOps and end-user apps share a server with different access</li><li>Showcase both DevOps tooling and end user application use cases</li></ul> |
| [2. Custom self-managed MCP servers](scenarios/2.%20Custom%20self-managed%20MCP%20servers/README.md) | <ul><li><b>Run your own FastMCP servers (exchange-rate and QuickChart) next to the ADK client</b></li><li>Connect one agent to multiple self-managed MCP servers over Streamable HTTP</li><li>Financial advisor client: convert any two currencies and chart historical rates when useful</li></ul> |
| [X. MCP Sandwich — WebMCP and ChromeDevTools MCP](scenarios/X.%20MCP%20Sandwich%20-%20WebMCP%20and%20ChromeDevTools%20MCP/README.md) | <ul><li>Configure ChromeDevTools MCP server</li><li>Run a web application that has live WebMCP tools registered on the browser</li><li>Load ChromeDevTools MCP, along with WebMCP hints as instructions on a "Simple" Agent</li><li><b>Load ChromeDevTools MCP, with WebMCP tools refreshed dynamically via context for the "Graph workflow" agent. It also features the Graph workflow of ADK 2.0, Human input via Human-In-The-Loop, and invocation context management.</b></li></ul> |


