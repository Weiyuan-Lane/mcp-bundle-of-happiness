import os
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION: str | None = os.getenv('SCENARIO_2_MODEL_VERSION')
EXCHANGE_RATE_MCP_URL: str | None = os.getenv('SCENARIO_2_MCP_SERVER_EXCHANGE_RATE_URL')
QUICKCHART_MCP_URL: str | None = os.getenv('SCENARIO_2_MCP_SERVER_QUICKCHART_URL')
# end -------------------------------------------------------------------------

SYSTEM_INSTRUCTION: str = '''\
You are a financial advisor.
Help the user convert any two currencies, look up current rates, and review historical exchange rates.

When a chart would make the result clearer (historical rates over time, or comparing more than one pair), call the QuickChart MCP and load the chart URL as image in the response so they can view it. A single spot conversion can stay as numbers.

Never guess, invent, or recall exchange rates or converted amounts. Always call the exchange-rate MCP tools first and answer only from those tool results. If a tool call fails or returns nothing, say so — do not fill in the gap.
'''

# Exchange rate MCP - current rates, conversions, and historical series
exchange_rate_mcp_toolset: McpToolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = EXCHANGE_RATE_MCP_URL,
    ),
)

# QuickChart MCP - render a chart image URL from Chart.js-compatible input
quickchart_mcp_toolset: McpToolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = QUICKCHART_MCP_URL,
    ),
)

tools: list[McpToolset] = [
    exchange_rate_mcp_toolset,
    quickchart_mcp_toolset,
]

root_agent: Agent = Agent(
    model = MODEL_VERSION,
    name = 'misconfigured_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = tools,
)
