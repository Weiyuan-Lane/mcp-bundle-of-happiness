# Scenario 3: MCP Toolbox for databases - custom MCP server

← [Back to MCP Bundle of Happiness](../../README.md)

![Scenario 3 gif](https://github.com/user-attachments/assets/bf5c2951-c185-403a-8020-422c48aceb57)

This scenario runs [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/) as a **custom MCP server** next to the ADK client. Toolbox turns YAML-declared SQL into tools over a local Postgres of dance clips.[^1]

The **dance trainer agent** asks whether you want a random clip, a genre, or a filming situation, then plays matching videos and lets you narrow by camera, music, choreography, or dancer.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App | Description | URL |
|---------------|-------------|-----|
| **ADK UI** | MCP test client — dance trainer agent below | [http://localhost:8080](http://localhost:8080) |
| **MCP Toolbox** | YAML-configured SQL tools over dance-clip Postgres | [http://localhost:8093/mcp](http://localhost:8093/mcp) |
| **MCP Toolbox UI** | Toolbox admin / tool explorer | [http://localhost:8082](http://localhost:8082) |
| **Keycloak** | Identity for 3-legged OAuth (`mcp-3lo` realm) | [http://keycloak.localhost:8081](http://keycloak.localhost:8081) |

## Dance trainer agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Connects over Streamable HTTP and lets the model call the tools |
| **Server** | [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/) | A small set of read tools against Postgres: `suggest_random_videos`, `list_videos_by_genre`, `list_videos_by_filming_situation`, plus dimension lists (`list_genres`, `list_filming_situations`, `list_camera_positions`, `list_music_tempos`, `list_choreographies`, `list_dancers`) |

The list is kept short so the agent can pick among them. Each dimension list still accepts optional `video_entries` filters and joins back to clips, so the same tools work whether the user is browsing everything or narrowing an existing pick.

(i.e. A fixed `list_camera_positions` tool might cause the agent to hallucinate - such as when trying to fetch all camera positions of a video, the agent might end up passing the camera position id of the existing video and no new value is created)

## Keycloak test users

The first tool call opens Keycloak. Sign in as one of these `mcp-3lo` users:

| Username | Password | What they can do |
|----------|----------|------------------|
| `admin` | `admin` | Every tool |
| `user` | `user` | Everything except `list_dancers` |
| `trial` | `trial` | Only `suggest_random_videos` |

ADK Web has no logout. **New Session** only clears the chat; the 3LO token stays in the ADK process, and Keycloak SSO stays in the browser.

To switch user, end the Keycloak session first:

[http://keycloak.localhost:8081/realms/mcp-3lo/protocol/openid-connect/logout](http://keycloak.localhost:8081/realms/mcp-3lo/protocol/openid-connect/logout)

Confirm logout there, then restart the ADK UI container (that drops the in-memory token). Start a new session and trigger a tool — you should get the Keycloak login again.

A new ADK credential bucket (`http://localhost:8080?userId=someone-else`) also forces ADK to re-auth, but without the logout URL Keycloak SSO still signs you back in as the same person.

----

#### Footnotes

[^1]: Clip metadata and videos come from the [AIST++ Dance Motion Dataset](https://google.github.io/aistplusplus_dataset/factsfigures.html), built on the AIST Dance Video Database (multi-genre, multi-dancer, multi-camera sequences).
