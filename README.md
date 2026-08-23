# MCP Bundle of Happiness

I have no idea why I named it as this. :grimacing:

## Setup

Make sure you clone with submodules
```
git clone --recurse-submodules git@github.com:Weiyuan-Lane/mcp-bundle-of-happiness.git
```

ChromeDevTools MCP is used for one of the scenarios, so make sure you use Chrome too
Install Chrome [here](https://www.google.com/chrome/)

Start and stop the servers with Make (this also opens Chrome with remote debugging for ChromeDevTools MCP):
```
make docker-compose-up
make docker-compose-down
```

## Scenarios

| Scenario | Lesson |
| --- | --- |
| [0. Simple MCP client and server setup](scenarios/0.%20Simple%20MCP%20client%20and%20server%20setup/README.md) | ADK client invokes a filesystem MCP server |
| [X. MCP Sandwich — WebMCP and ChromeDevTools MCP](scenarios/X.%20MCP%20Sandwich%20-%20WebMCP%20and%20ChromeDevTools%20MCP/README.md) | Invoke chrome-devtools-mcp to reach WebMCP (Double MCP!), and also explore graphing flow of ADK 2.0 |


