import os
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams, StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION = os.getenv('SCENARIO_1_MODEL_VERSION')
SUPABASE_URL = os.getenv('SCENARIO_1_SUPABASE_URL')
SUPABASE_TOKEN = os.getenv('SCENARIO_1_SUPABASE_TOKEN')
MCP_SERVER_FILESYSTEM_VERSION = os.getenv('SCENARIO_1_MCP_SERVER_FILESYSTEM_VERSION')
MIGRATIONS_DIRECTORY_PATH = os.getenv('SCENARIO_1_MIGRATIONS_DIRECTORY_PATH')
# end -------------------------------------------------------------------------

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MIGRATIONS_DIRECTORY_PATH)

SYSTEM_INSTRUCTION = '''\
    You are a DevOps agent.
    You are responsible for managing the database.
    You can manage the database, such as listing tables, extensions, and applying migrations (together with the filesystem MCP tools).

    Never guess, invent, or recall file names, contents, or directory structure. Always call the filesystem MCP tools first and answer only from those tool results. If a tool call fails or returns nothing, say so — do not fill in the gap.
'''

filesystem_mcp_toolset = McpToolset(
    connection_params = StdioConnectionParams(
        server_params = StdioServerParameters(
            command = 'npx',
            args = [
                "-y",
                f"@modelcontextprotocol/server-filesystem@{MCP_SERVER_FILESYSTEM_VERSION}",
                os.path.abspath(TARGET_FOLDER_PATH),
            ],
        ),
    ),
    tool_filter = [
        'read_text_file',
        'read_multiple_files',
        'list_directory',
        'list_directory_with_sizes',
        'search_files',
        'directory_tree',
        'get_file_info',
        'list_allowed_directories',
    ],
)

supabase_mcp_toolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = SUPABASE_URL,
        headers = {
            "Authorization": f"Bearer {SUPABASE_TOKEN}",
        }
    ),
    tool_filter = [
        'list_tables',
        'list_extensions',
        'list_migrations',
        'apply_migration',
        'execute_sql',
    ],
)

root_agent = Agent(
    model = MODEL_VERSION,
    name = 'devops_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = [
        filesystem_mcp_toolset,
        supabase_mcp_toolset,
    ]
)
