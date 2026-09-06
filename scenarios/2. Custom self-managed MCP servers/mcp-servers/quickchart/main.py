import json
import os
from typing import Any, TypedDict

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from starlette.requests import Request
from starlette.responses import JSONResponse

load_dotenv()

# Get environment variables ---------------------------------------------------
HOST: str = os.getenv("SCENARIO_2_MCP_SERVER_QUICKCHART_HOST", "localhost")
PORT: int = int(os.getenv("SCENARIO_2_MCP_SERVER_QUICKCHART_PORT", "8000"))
KEYCLOAK_JWKS_URI: str = os.environ["SCENARIO_2_KEYCLOAK_JWKS_URI"]
KEYCLOAK_ISSUER: str = os.environ["SCENARIO_2_KEYCLOAK_ISSUER"]
KEYCLOAK_CLIENT_CUSTOM_MCP_QUICKCHART_ID: str = os.environ["SCENARIO_2_KEYCLOAK_CLIENT_CUSTOM_MCP_QUICKCHART_ID"]
QUICKCHART_SCOPE: str = os.environ["SCENARIO_2_KEYCLOAK_SCOPE_QUICKCHART"]
# end -------------------------------------------------------------------------

QUICKCHART_HOST = "https://quickchart.io/chart"

mcp = FastMCP(
    "Charting MCP Server",
    auth = JWTVerifier(
        jwks_uri = KEYCLOAK_JWKS_URI,
        issuer = KEYCLOAK_ISSUER,
        audience = KEYCLOAK_CLIENT_CUSTOM_MCP_QUICKCHART_ID,
        required_scopes = [QUICKCHART_SCOPE],
    ),
)

class ErrorResult(TypedDict):
    error: str

class ChartResult(TypedDict):
    request_uri: str

@mcp.custom_route("/health", methods=["GET"])
async def liveness_check(request: Request) -> JSONResponse:
    """Liveness probe endpoint for health checks"""
    return JSONResponse({})

@mcp.tool
async def make_chart(input: dict[str, Any]) -> ChartResult | ErrorResult:
    """Use this to make a chart image and return it

    Args:
        input: A QuickChart.io compatible dict to make chart from (See example below). This must be a valid dict input.

    Example:
    {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May'],
            datasets: [
            {
                label: 'Dogs',
                data: [50, 60, 70, 180, 190],
                fill: false,
                borderColor: 'blue'
            },
            {
                label: 'Cats',
                data: [100, 200, 300, 400, 500],
                fill: false,
                borderColor: 'green'
            }
            ]
        }
    }

    Returns:
        A dict with the QuickChart request URI for the generated chart
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                QUICKCHART_HOST,
                params={"c": json.dumps(input)},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"error": f"API request failed with error: {exc}"}
    except Exception as exc:
        return {"error": f"API request failed with error: {exc}"}

    return {"request_uri": str(response.url)}

if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
