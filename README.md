# MCP Bundle of Happiness

I have no idea why I named it as this. :grimacing:

## Setup

1. Make sure you clone with submodules
```
git clone --recurse-submodules git@github.com:Weiyuan-Lane/mcp-bundle-of-happiness.git
```

2. ChromeDevTools MCP is used for one of the scenarios, so make sure you use Chrome too.

Install Chrome [here](https://www.google.com/chrome/)

3. Duplicate `.env.sample` to `.env`, and fill in the missing values

4. Finally, start and stop the all scenarios with make commands (this also opens Chrome with remote debugging for ChromeDevTools MCP):
```
make docker-compose-up          # Start
make docker-compose-down        # Stop
```

## Scenarios

| Scenario | Thumbnail | Lesson(s) |
| --- | --- | --- |
| [0. Simple MCP client and server setup](scenarios/0.%20Simple%20MCP%20client%20and%20server%20setup/README.md) | [![Scenario 1](https://github.com/user-attachments/assets/94376955-bf1f-465a-9e0f-d25e3b4db7ab)](scenarios/0.%20Simple%20MCP%20client%20and%20server%20setup/README.md) | <ul><li><b>Configure a simple filesystem MCP server</b></li><li>Setup a MCP client using an agent built in ADK 2.0</li></ul> |
| [1. Managed MCP client setup and server connections](scenarios/1.%20Managed%20MCP%20client%20and%20server%20connections/README.md) | [](scenarios/1.%20Managed%20MCP%20client%20and%20server%20connections/README.md) | <ul><li><b>Connect to managed MCP servers provided by other services (Google Maps, Supabase)</b></li><li><b>Static auth - configure an auth token or API key to access an MCP server</b></li><li>Configure multiple MCP servers within one agent</li><li>Filter tools per agent so DevOps and end-user apps share a server with different access</li><li>Showcase both DevOps tooling and end user application use cases</li></ul> |
| [2. Custom self-managed MCP servers](scenarios/2.%20Custom%20self-managed%20MCP%20servers/README.md) | [](scenarios/2.%20Custom%20self-managed%20MCP%20servers/README.md) | <ul><li><b>Run your own custom MCP servers (exchange-rate and QuickChart) next to the ADK client</b></li><li><b>2-legged OAuth — ADK exchanges client credentials at Keycloak; each MCP server verifies the JWT audience and scope</b></li><li>Connect one agent to multiple self-managed MCP servers over Streamable HTTP</li></ul> |
| [3. MCP Toolbox for databases - custom MCP server](scenarios/3.%20MCP%20Toolbox%20for%20databases%20-%20custom%20MCP%20server/README.md) | [](scenarios/3.%20MCP%20Toolbox%20for%20databases%20-%20custom%20MCP%20server/README.md) | <ul><li><b>Run MCP Toolbox for Databases as a easy YAML-configured MCP server wrapping around a database</b></li><li><b>3-legged OAuth — ADK opens Keycloak login; Toolbox verifies the JWT audience and per-tool scopes</b></li><li>Role-based tool access: `admin` / `user` / `trial` accounts get different scopes</li></ul> |
| [X. MCP Sandwich — WebMCP and ChromeDevTools MCP](scenarios/X.%20MCP%20Sandwich%20-%20WebMCP%20and%20ChromeDevTools%20MCP/README.md) | [](scenarios/X.%20MCP%20Sandwich%20-%20WebMCP%20and%20ChromeDevTools%20MCP/README.md) | <ul><li>Configure ChromeDevTools MCP server</li><li>Run a web application that has live WebMCP tools registered on the browser</li><li>Load ChromeDevTools MCP, along with WebMCP hints as instructions on a "Simple" Agent</li><li><b>Load ChromeDevTools MCP, with WebMCP tools refreshed dynamically via context for the "Graph workflow" agent. It also features the Graph workflow of ADK 2.0, Human input via Human-In-The-Loop, and invocation context management.</b></li></ul> |

### Local servers

| Name                      | URL                                   | Scenario                                               | Description                                                            |
|---------------------------|---------------------------------------|--------------------------------------------------------|------------------------------------------------------------------------|
| ADK UI                    | [http://localhost:8080](http://localhost:8080)                   | -                                                      | Main ADK UI app for managing and running MCP clients/scenarios         |
| Keycloak (Identity/OAuth) | [http://keycloak.localhost:8081](http://keycloak.localhost:8081) | -                                                      | Keycloak IAM; `mcp-2lo` (2-legged) and `mcp-3lo` (3-legged) realms — ADK caller, MCP servers as audiences |
| Exchange Rate MCP Server  | [http://localhost:8091](http://localhost:8091)                   | 2. Custom self-managed MCP servers                     | Custom MCP server offering exchange rate functionality                 |
| QuickChart MCP Server     | [http://localhost:8092](http://localhost:8092)                   | 2. Custom self-managed MCP servers                     | Custom MCP server providing chart/graph image generation               |
| MCP Toolbox               | [http://localhost:8093](http://localhost:8093)                   | 3. MCP Toolbox for databases - custom MCP server       | YAML-configured SQL tools over dance-clip Postgres                     |
| MCP Toolbox UI            | [http://localhost:8082](http://localhost:8082)                   | 3. MCP Toolbox for databases - custom MCP server       | Toolbox admin / tool explorer UI                                       |
| Demo WebMCP Server        | [http://localhost:8090](http://localhost:8090)                   | X. MCP Sandwich — WebMCP and ChromeDevTools MCP        | Demo web server to showcase WebMCP tools in the browser               |

_Note: If you changed any ports in your `.env`, the actual URL may differ!_


