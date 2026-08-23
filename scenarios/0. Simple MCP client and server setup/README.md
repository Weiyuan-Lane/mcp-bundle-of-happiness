# Scenario 0: Simple MCP client and server setup

← [Back to MCP Bundle of Happiness](../../README.md)

This scenario is the smallest useful MCP loop: an ADK agent as the **client**, and the official filesystem MCP package as the **server**, started on demand with **npx**.

The agent can list, read, and manage files only inside `mcp-directory/`. It never invents paths or contents — it always calls the filesystem tools first.

## MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` on `filesystem_assistant_agent` | Starts the server process, lists its tools, and calls them on the user's behalf |
| **Server** | `@modelcontextprotocol/server-filesystem` | Exposes filesystem tools (`list`, `read`, `write`, …) scoped to one folder |

The client is the process that *invokes* the server. The server is the process that *implements* the tools.
