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
| [0. Simple MCP client and server setup](scenarios/0.%20Simple%20MCP%20client%20and%20server%20setup/README.md) | <ul><li>Configure a filesystem MCP server</li><li>Setup a MCP client using an agent built in ADK 2.0</li></ul> |
| [X. MCP Sandwich — WebMCP and ChromeDevTools MCP](scenarios/X.%20MCP%20Sandwich%20-%20WebMCP%20and%20ChromeDevTools%20MCP/README.md) | <ul><li>Configure ChromeDevTools MCP server</li><li>Run a web application that has live WebMCP tools registered on the browser</li><li>Load ChromeDevTools MCP, along with WebMCP hints as instructions on a "Simple" Agent</li><li>Load ChromeDevTools MCP, with WebMCP tools refreshed dynamically via context for the "Graph workflow" agent. It also features the Graph workflow of ADK 2.0, Human input via Human-In-The-Loop, and invocation context management.</li></ul> |


