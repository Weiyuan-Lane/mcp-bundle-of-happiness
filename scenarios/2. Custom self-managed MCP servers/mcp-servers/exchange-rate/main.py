import os
from typing import Any, TypeIs, TypedDict, cast

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

load_dotenv()

HOST: str = os.getenv("HOST", "localhost")
PORT: int = int(os.getenv("PORT", "8000"))

mcp = FastMCP("Currency MCP Server")
CURRENCY_API_HOST = "https://api.frankfurter.app"  # IF this doesn't work, try https://api.frankfurter.dev/v1

class ErrorResult(TypedDict):
    error: str

class CurrencyRates(TypedDict):
    amount: float
    base: str
    date: str
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

async def _frankfurter_get(path: str, params: dict[str, str]) -> JsonObject | ErrorResult:
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

    if not isinstance(data, dict):
        return {"error": f"API request failed with invalid response body as: {data}"}
    if "message" in data:
        return {"error": f"API request failed with error: {data['message']}"}
    return data

def _is_error(data: JsonObject | ErrorResult) -> TypeIs[ErrorResult]:
    return "error" in data and "rates" not in data

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
    data = await _frankfurter_get("latest", {"base": currency.upper()})
    if _is_error(data):
        return data
    return cast(CurrencyRates, data)

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

    data = await _frankfurter_get(
        "latest",
        {"from": from_currency_upper, "to": to_currency_upper},
    )
    if _is_error(data):
        return data

    rates = data.get("rates")
    if not isinstance(rates, dict) or to_currency_upper not in rates:
        return {
            "error": (
                "API request failed with missing exchange rate data for: "
                f"{from_currency_upper} --> {to_currency_upper}"
            )
        }

    exchange_rate = float(rates[to_currency_upper])
    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
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
        f"{start_date}..{end_date}",
        {"base": from_currency_upper, "symbols": to_currency_upper},
    )
    if _is_error(data):
        return data

    rates = data.get("rates")
    if not isinstance(rates, dict):
        return {"error": "API request failed with missing time series data"}

    exchange_rates: dict[str, float] = {}
    for date, rate in rates.items():
        if not isinstance(rate, dict) or to_currency_upper not in rate:
            return {"error": "API request failed with missing time series data"}
        exchange_rates[str(date)] = float(rate[to_currency_upper])

    return {
        "from_currency": from_currency_upper,
        "to_currency": to_currency_upper,
        "exchange_rates": exchange_rates,
    }

if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
