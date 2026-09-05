import os
from typing import Any, TypeIs, TypedDict

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from starlette.requests import Request
from starlette.responses import JSONResponse

load_dotenv()

# Get environment variables ---------------------------------------------------
HOST: str = os.getenv("SCENARIO_2_MCP_SERVER_EXCHANGE_RATE_HOST", "localhost")
PORT: int = int(os.getenv("SCENARIO_2_MCP_SERVER_EXCHANGE_RATE_PORT", "8000"))
KEYCLOAK_JWKS_URI: str = os.environ["KEYCLOAK_JWKS_URI"]
KEYCLOAK_ISSUER: str = os.environ["KEYCLOAK_ISSUER"]
KEYCLOAK_CLIENT_CUSTOM_MCP_EXCHANGE_RATE_ID: str = os.environ["SCENARIO_2_KEYCLOAK_CLIENT_CUSTOM_MCP_EXCHANGE_RATE_ID"]
EXCHANGE_RATE_SCOPE: str = os.environ["SCENARIO_2_KEYCLOAK_SCOPE_EXCHANGE_RATE"]
# end -------------------------------------------------------------------------

CURRENCY_API_HOST = "https://api.frankfurter.dev"

mcp = FastMCP(
    "Currency MCP Server",
    auth = JWTVerifier(
        jwks_uri = KEYCLOAK_JWKS_URI,
        issuer = KEYCLOAK_ISSUER,
        audience = KEYCLOAK_CLIENT_CUSTOM_MCP_EXCHANGE_RATE_ID,
        required_scopes = [EXCHANGE_RATE_SCOPE],
    ),
)

class ErrorResult(TypedDict):
    error: str

class CurrencyRates(TypedDict):
    base: str
    rates: dict[str, float]

class ConversionResult(TypedDict):
    from_currency: str
    to_currency: str
    exchange_rate: float
    converted_amount: float

class TimeSeriesResult(TypedDict):
    from_currency: str
    to_currency: str
    exchange_rates: dict[str, float]

type JsonObject = dict[str, Any]
type JsonValue = JsonObject | list[Any]

async def _frankfurter_get(path: str, params: dict[str, str] | None = None) -> JsonValue | ErrorResult:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CURRENCY_API_HOST}/{path}", params=params)
            data: Any = response.json()
    except httpx.HTTPError as exc:
        return {"error": f"API request failed with error: {exc}"}
    except ValueError:
        return {"error": "API request failed with invalid JSON response"}
    except Exception as exc:
        return {"error": f"API request failed with error: {exc}"}

    if isinstance(data, dict) and "message" in data:
        return {"error": f"API request failed with error: {data['message']}"}
    if not response.is_success:
        return {"error": f"API request failed with status {response.status_code}"}
    if not isinstance(data, (dict, list)):
        return {"error": f"API request failed with invalid response body as: {data}"}
    return data

def _is_error(data: JsonValue | ErrorResult) -> TypeIs[ErrorResult]:
    return isinstance(data, dict) and "error" in data

def _rates_lookup(rows: list[Any]) -> dict[str, float] | ErrorResult:
    rates: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, dict) or "quote" not in row or "rate" not in row:
            return {"error": "API request failed with invalid rate row"}
        rates[str(row["quote"])] = float(row["rate"])
    return rates

@mcp.custom_route("/health", methods=["GET"])
async def liveness_check(request: Request) -> JSONResponse:
    """Liveness probe endpoint for health checks"""
    return JSONResponse({})

@mcp.tool
async def get_currency_data(currency: str) -> CurrencyRates | ErrorResult:
    """Use this to get current data of a currency.

    Args:
        currency: The target currency to get data for (e.g., "USD").

    Returns:
        A dict for the currency data
    """
    currency_upper = currency.upper()
    data = await _frankfurter_get("v2/rates", {"base": currency_upper})
    if _is_error(data):
        return data
    if not isinstance(data, list):
        return {"error": "API request failed with invalid rates response"}

    rates = _rates_lookup(data)
    if _is_error(rates):
        return rates
    return {"base": currency_upper, "rates": rates}

@mcp.tool
async def convert_from_one_currency_to_another_currency(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0,
) -> ConversionResult | ErrorResult:
    """Use this to calculate exchange_rate from one currency to another currency.

    Args:
        from_currency: The original currency to convert from (e.g., "USD").
        to_currency: The new currency to convert to (e.g., "EUR").
        amount: The amount of the original currency to convert. Default to 1.0 if not provided.

    Returns:
        A dict for the exchange rate outcome
    """
    from_currency_upper = from_currency.upper()
    to_currency_upper = to_currency.upper()

    data = await _frankfurter_get(f"v2/rate/{from_currency_upper}/{to_currency_upper}")
    if _is_error(data):
        return data
    if not isinstance(data, dict) or "rate" not in data:
        return {
            "error": (
                "API request failed with missing exchange rate data for: "
                f"{from_currency_upper} --> {to_currency_upper}"
            )
        }

    exchange_rate = float(data["rate"])
    return {
        "from_currency": from_currency_upper,
        "to_currency": to_currency_upper,
        "exchange_rate": exchange_rate,
        "converted_amount": exchange_rate * amount,
    }

@mcp.tool
async def exchange_rate_time_series_data(
    from_currency: str,
    to_currency: str,
    start_date: str,
    end_date: str,
) -> TimeSeriesResult | ErrorResult:
    """Use this to obtain time series (or historical) data from one currency to another currency, across two given dates.

    Args:
        from_currency: The original currency to convert from (e.g., "USD").
        to_currency: The new currency to convert to (e.g., "EUR").
        start_date: The start date for the time series in YYYY-MM-DD format (e.g., "2024-01-01").
        end_date: The end date for the time series in YYYY-MM-DD format (e.g., "2024-01-01").

    Returns:
        A dict for time series data on the exchange rate between the two currencies
    """
    from_currency_upper = from_currency.upper()
    to_currency_upper = to_currency.upper()

    data = await _frankfurter_get(
        "v2/rates",
        {
            "base": from_currency_upper,
            "quotes": to_currency_upper,
            "from": start_date,
            "to": end_date,
        },
    )
    if _is_error(data):
        return data
    if not isinstance(data, list):
        return {"error": "API request failed with missing time series data"}

    exchange_rates: dict[str, float] = {}
    for row in data:
        if not isinstance(row, dict) or "date" not in row or "rate" not in row:
            return {"error": "API request failed with missing time series data"}
        exchange_rates[str(row["date"])] = float(row["rate"])

    return {
        "from_currency": from_currency_upper,
        "to_currency": to_currency_upper,
        "exchange_rates": exchange_rates,
    }

if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
