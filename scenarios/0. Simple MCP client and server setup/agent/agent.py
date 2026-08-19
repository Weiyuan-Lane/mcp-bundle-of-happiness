import os
from google.adk import Agent
from google.adk import Workflow
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
FOLDER_DIRECTORY = os.getenv('SCENARIO_0_FOLDER_DIRECTORY')
MODEL_VERSION = os.getenv('SCENARIO_0_MODEL_VERSION')
# end -------------------------------------------------------------------------

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), FOLDER_DIRECTORY)

SYSTEM_INSTRUCTION = '''\
Help the user manage their files.
You can list, read and manage files only in the selected folder. Show the directory structure as a tree (not JSON) — folders and files nested by indentation
However, you should ignore the .keep file for all operations (both read and write), but don't mention to the user you are ignoring it.
'''

filesystem_assistant_agent = Agent(
    model = MODEL_VERSION,
    name = 'filesystem_assistant_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = [
        McpToolset(
            connection_params = StdioConnectionParams(
                server_params = StdioServerParameters(
                    command = 'npx',
                    args = [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
        )
    ],
)

root_agent = Workflow(
    name = 'root_agent',
    edges = [
        ('START', filesystem_assistant_agent),
    ],
)
