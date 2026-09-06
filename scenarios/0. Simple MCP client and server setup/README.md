# Scenario 0: Simple MCP client and server setup

← [Back to MCP Bundle of Happiness](../../README.md)

![Scenario 0 gif](https://github.com/user-attachments/assets/808d0437-ea59-45c7-afe5-ccf620edb227)

This scenario is the smallest useful MCP loop: an ADK agent as the **client**, and the official filesystem MCP package as the **server**, started on demand with **npx**.

The agent can list, read, and manage files only inside `mcp-directory/`. It never invents paths or contents — it always calls the filesystem tools first.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App | Description                                                            | URL                           |
|---------------|------------------------------------------------------------------------|-------------------------------|
| **ADK UI**    | MCP test client - Contain agent with MCP setup below  | [http://localhost:8080](http://localhost:8080) |

## MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Starts the server process, lists its tools, and calls them on the user's behalf |
| **Server** | `@modelcontextprotocol/server-filesystem` | Exposes filesystem tools (`list`, `read`, `write`, …) scoped to one folder |
