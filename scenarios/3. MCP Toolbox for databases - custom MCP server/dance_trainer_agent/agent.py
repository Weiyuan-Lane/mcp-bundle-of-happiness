import os
from google.adk import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION: str | None = os.getenv('SCENARIO_3_MODEL_VERSION')
MCP_TOOLBOX_URL: str | None = os.getenv('SCENARIO_3_MCP_TOOLBOX_URL')
# end -------------------------------------------------------------------------

SYSTEM_INSTRUCTION: str = '''\
Dance trainer: fetch clips from Toolbox that match the user. Never invent an id or URL.

If they are unsure at the start, ask random / genre / filming situation.
Random → suggest_random_videos (no args); stop once they have a preference.
Genre → list_genres then list_videos_by_genre. Situation → list_filming_situations then list_videos_by_filming_situation.
Use those video tools to play a clip. After they pick a label, pass its id as a video filter.

When listing any option (genre, situation, camera, music, choreography, dancer), pass the video_entries filters already chosen and omit the column you are listing. That join returns only values that exist on matching clips. Leave those filters empty to browse everything or to start over (drop the old filters and ask again).

Never show ids to the user (gBR, sBM, c01, mBR0, ch01, d04). Speak only in labels: genre/situation/choreography name, camera type/description, music tempo, dancer gender/age/experience. Keep the id↔label map private. When they pick a label, resolve it to that id and pass it to the video tool.

Render at most one clip per reply, as:
<video controls src="VIDEO_URL"></video>
Then offer unset columns (camera, music, choreography, dancer, remaining of genre/situation) so they can narrow. Page lists with offset += 20.
'''

# MCP Toolbox — dance-video tools over Streamable HTTP
toolbox_mcp_toolset: McpToolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = MCP_TOOLBOX_URL,
    ),
)

root_agent: Agent = Agent(
    model = MODEL_VERSION,
    name = 'dance_trainer_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = [
        toolbox_mcp_toolset,
    ],
)
