import os
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk import Agent
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from dotenv import load_dotenv
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION: str | None = os.getenv('SCENARIO_3_MODEL_VERSION')
MCP_TOOLBOX_URL: str | None = os.getenv('SCENARIO_3_MCP_TOOLBOX_URL')
KEYCLOAK_ISSUER: str | None = os.getenv('SCENARIO_3_KEYCLOAK_ISSUER')
KEYCLOAK_PUBLIC_ISSUER: str | None = os.getenv('SCENARIO_3_KEYCLOAK_PUBLIC_ISSUER')
KEYCLOAK_CLIENT_ADK_3LO_ID: str | None = os.getenv('SCENARIO_3_KEYCLOAK_CLIENT_ADK_3LO_ID')
KEYCLOAK_CLIENT_ADK_3LO_SECRET: str | None = os.getenv('SCENARIO_3_KEYCLOAK_CLIENT_ADK_3LO_SECRET')
# end -------------------------------------------------------------------------

oauth2_scheme: OAuth2 = OAuth2(
    flows = OAuthFlows(
        authorizationCode = OAuthFlowAuthorizationCode(
            authorizationUrl = f'{KEYCLOAK_PUBLIC_ISSUER}/protocol/openid-connect/auth',
            tokenUrl = f'{KEYCLOAK_ISSUER}/protocol/openid-connect/token',
            scopes = {
                'openid': 'Sign in to MCP Toolbox',
            },
        ),
    ),
)
oauth2_credential: AuthCredential = AuthCredential(
    auth_type = AuthCredentialTypes.OAUTH2,
    oauth2 = OAuth2Auth(
        client_id = KEYCLOAK_CLIENT_ADK_3LO_ID,
        client_secret = KEYCLOAK_CLIENT_ADK_3LO_SECRET,
    ),
)

SYSTEM_INSTRUCTION: str = '''\
Dance trainer: fetch clips from Toolbox that match the user. Never invent an id or URL.

The user must sign in. Their Keycloak account decides which tools work:
- trial: only suggest_random_videos
- user: everything except list_dancers
- admin: every tool

If a tool returns unauthorized / forbidden / insufficient_scope, do not retry it.
Tell them their account cannot do that, and stay on tools that succeeded.

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

toolbox_mcp_toolset: McpToolset = McpToolset(
    connection_params = StreamableHTTPConnectionParams(
        url = MCP_TOOLBOX_URL,
    ),
    auth_scheme = oauth2_scheme,
    auth_credential = oauth2_credential,
)

root_agent: Agent = Agent(
    model = MODEL_VERSION,
    name = 'dance_trainer_agent',
    instruction = SYSTEM_INSTRUCTION,
    tools = [
        toolbox_mcp_toolset,
    ],
)
