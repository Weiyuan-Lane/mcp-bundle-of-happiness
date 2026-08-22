import os
from google.adk import Agent
from google.adk import Context
from google.adk import Event
from google.adk import Workflow
from google.adk.events import RequestInput
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.workflow import FunctionNode
from mcp import StdioServerParameters
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION = os.getenv('SCENARIO_X_MODEL_VERSION')
MCP_SERVER_CHROMEDEVTOOLS_VERSION = os.getenv('SCENARIO_X_MCP_SERVER_CHROMEDEVTOOLS_VERSION')
CHROME_DEBUGGING_PORT = os.getenv('SCENARIO_X_CHROME_DEBUGGING_PORT')
CHROME_DEBUGGING_ADDR = os.getenv('SCENARIO_X_CHROME_DEBUGGING_ADDR')
# end -------------------------------------------------------------------------


# Simple Chrome DevTools MCP client flow --------------------------------------
SYSTEM_INSTRUCTION = '''\
Only call tools that appear in your tool list. Never invent names.

Page WebMCP tools are not callable directly. After navigating:
1. list_webmcp_tools
2. execute_webmcp_tool with that exact name and JSON arguments
If a tool call fails or no tools are listed, say so. Do not pretend you used a tool.
'''

chrome_devtools_mcp_client = McpToolset(
    connection_params = StdioConnectionParams(
        server_params = StdioServerParameters(
            command = 'npx',
            args = [
                "-y",
                f"chrome-devtools-mcp@{MCP_SERVER_CHROMEDEVTOOLS_VERSION}",
                f"--browser-url=http://{CHROME_DEBUGGING_ADDR}:{CHROME_DEBUGGING_PORT}",
                "--categoryExperimentalWebmcp=true",
            ],
        ),
        timeout = 60.0,
    ),
)

root_agent = Agent(
    model = MODEL_VERSION,
    name = 'chrome_devtools_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = [chrome_devtools_mcp_client],
)
# end -------------------------------------------------------------------------


# chrome_devtools_mcp_client = McpToolset(
#     connection_params = StdioConnectionParams(
#         server_params = StdioServerParameters(
#             command = 'npx',
#             args = [
#                 "-y",
#                 f"chrome-devtools-mcp@{MCP_SERVER_CHROMEDEVTOOLS_VERSION}",
#                 f"--browser-url=http://{CHROME_DEBUGGING_ADDR}:{CHROME_DEBUGGING_PORT}",
#                 "--categoryExperimentalWebmcp=true",
#             ],
#         ),
#     ),
#     tool_filter = [
#         'list_webmcp_tools',
#         'execute_webmcp_tool',
#     ],
# )

# browser_interaction_agent = Agent(
#     model = MODEL_VERSION,
#     name = 'chrome_devtools_agent',
#     instruction = SYSTEM_INSTRUCTION,
#     tools = [chrome_devtools_mcp_client],
# )

# root_agent = Workflow(
#     name = 'root_agent',
#     edges = [
#         ('START', browser_interaction_agent, browser_interaction_router),
#         (browser_interaction_router,
#             {
#                 'ask_user_for_action': ask_user_for_action_node,
#                 'open_page': open_page_node,
#                 'select_page': select_page_node,
#                 'interact_with_webmcp_tool': interact_with_webmcp_tool_node,
#             }
#         )
#     ],
# )
