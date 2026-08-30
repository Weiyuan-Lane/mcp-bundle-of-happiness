# Scenario X: MCP Sandwich — WebMCP and Chrome DevTools MCP

← [Back to MCP Bundle of Happiness](../../README.md)

This scenario sandwiches two MCP layers: an ADK agent as the **client**, and `chrome-devtools-mcp` as the **server**, started on demand with **npx**. Page-exposed WebMCP tools are reached only through that server.

The agent opens, lists, and selects Chrome pages, then lists and runs WebMCP tools on the selected page.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App        | Description                                                            | URL                        |
|----------------------|------------------------------------------------------------------------|----------------------------|
| **ADK UI**           | MCP test client - Contain both Simple and Graph workflow agents below  | [http://localhost:8080](http://localhost:8080) |
| **Web application**  | App with registered WebMCP tools (the web application)                 | [http://localhost:8090](http://localhost:8090) |

Access these URLs in your browser to interact with the agent interface and the demo web application that exposes WebMCP tools.

## Simple Agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` on `chrome_devtools_agent` | Starts the server process, lists its tools, and lets the model call them |
| **Server** | `chrome-devtools-mcp` | Browser tools plus `list_webmcp_tools` / `execute_webmcp_tool` for the selected page |

The client is the process that *invokes* the server. The model calls those tools directly.

## Graph workflow Agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | `McpToolset` in `utils.py`, called from graph's nodes | Action nodes invoke named tools (`new_page`, `select_page`, `execute_webmcp_tool`, …) directly, instead of binding the MCP client to the agents |
| **Server** | `chrome-devtools-mcp` (same npx process) | Same browser and WebMCP tools; the model never holds the toolset |

The graph is the process that *invokes* the server. Two agents are used here but only to classify intent — they do not call MCP themselves.

## Extras

A `SKILL.md` is also added if you want to load that into your local agents / CLI (such as Claude Code or Antigravity)

I've also added it as a Claude plugin [here](https://github.com/Weiyuan-Lane/shareable-claude/tree/feature/mcp-sandwich-config/packages/personal) containing both the same `SKILL.md` and the `.mcp.json` config for ChromeDevTools MCP. Simply clone the repository and run the associated makefile commands to install the `personal` package for your local client use case
