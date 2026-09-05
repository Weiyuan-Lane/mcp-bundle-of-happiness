import os
from .instructions import base_instructions, supabase_replacement_instructions
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION: str | None = os.getenv('SCENARIO_1_MODEL_VERSION')
GOOGLE_MAPS_URL: str | None = os.getenv('SCENARIO_1_GOOGLE_MAPS_URL')
GOOGLE_MAPS_API_KEY: str | None = os.getenv('SCENARIO_1_GOOGLE_MAPS_API_KEY')
SUPABASE_URL: str | None = os.getenv('SCENARIO_1_SUPABASE_URL')
SUPABASE_TOKEN: str | None = os.getenv('SCENARIO_1_SUPABASE_TOKEN')
# end -------------------------------------------------------------------------

SYSTEM_INSTRUCTION: str = base_instructions

# Google Maps MCP - Search places, Lookup Weather, Compute routes
# See the list of tools here: https://developers.google.com/maps/ai/grounding-lite#tools
maps_mcp_toolset: McpToolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = GOOGLE_MAPS_URL,
        headers = {
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    )
)

tools: list[McpToolset] = [maps_mcp_toolset]

# Optional - Query Supabase database for hotel and airport stats
if SUPABASE_TOKEN:
    supabase_mcp_toolset: McpToolset = McpToolset(
        connection_params = StreamableHTTPConnectionParams(
            url = SUPABASE_URL,
            headers = {
                "Authorization": f"Bearer {SUPABASE_TOKEN}",
            }
        ),
        tool_filter = [
            'execute_sql',
        ],
    )
    tools.append(supabase_mcp_toolset)
    SYSTEM_INSTRUCTION = supabase_replacement_instructions

root_agent: Agent = Agent(
    model = MODEL_VERSION,
    name = 'travel_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = tools,
)
