# Scenario 3: MCP Toolbox for databases - custom MCP server

← [Back to MCP Bundle of Happiness](../../README.md)

This scenario runs [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/) as a **custom MCP server** next to the ADK client. Toolbox turns YAML-declared SQL into tools over a local Postgres of dance clips.

The **dance trainer agent** asks whether you want a random clip, a genre, or a filming situation, then plays matching videos and lets you narrow by camera, music, choreography, or dancer.

## What runs on `make docker-compose-up`

When you start this scenario with `make docker-compose-up`, the following services are accessible:

| Service / App | Description | URL |
|---------------|-------------|-----|
| **ADK UI** | MCP test client — dance trainer agent below | [http://localhost:8080](http://localhost:8080) |
| **MCP Toolbox** | YAML-configured SQL tools over dance-clip Postgres | [http://localhost:8093/mcp](http://localhost:8093/mcp) |
| **MCP Toolbox UI** | Toolbox admin / tool explorer | [http://localhost:8082](http://localhost:8082) |

## Dance trainer agent MCP configuration

| Role | In this scenario | What it does |
| --- | --- | --- |
| **Client** | Google ADK `McpToolset` | Connects over Streamable HTTP and lets the model call the tools |
| **Server** | [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/) | A small set of read tools against Postgres: `suggest_random_videos`, `list_videos_by_genre`, `list_videos_by_filming_situation`, plus dimension lists (`list_genres`, `list_filming_situations`, `list_camera_positions`, `list_music_tempos`, `list_choreographies`, `list_dancers`) |

The list is kept short so the agent can pick among them. Each dimension list still accepts optional `video_entries` filters and joins back to clips, so the same tools work whether the user is browsing everything or narrowing an existing pick.

(i.e. A fixed `list_camera_positions` tool might cause the agent to hallucinate - such as when trying to fetch all camera positions of a video, the agent might end up passing the camera position id of the existing video and no new value is created)

