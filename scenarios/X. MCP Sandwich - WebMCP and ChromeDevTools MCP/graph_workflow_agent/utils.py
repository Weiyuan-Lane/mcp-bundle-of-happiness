import json
import os
import re
from typing import Any
from google.adk import Context
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
from .constants import RestartReason, STATE_PAGES, STATE_WEBMCP_TOOLS
load_dotenv()

MCP_SERVER_CHROMEDEVTOOLS_VERSION: str | None = os.getenv('SCENARIO_X_MCP_SERVER_CHROMEDEVTOOLS_VERSION')
CHROME_DEBUGGING_PORT: str | None = os.getenv('SCENARIO_X_CHROME_DEBUGGING_PORT')
CHROME_DEBUGGING_ADDR: str | None = os.getenv('SCENARIO_X_CHROME_DEBUGGING_ADDR')

chrome_devtools_mcp_client: McpToolset = McpToolset(
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

def as_text(value: object) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n'.join(part for part in (as_text(item) for item in value) if part)
    if isinstance(value, dict):
        content = value.get('content')
        if content is not None:
            extracted = as_text(content)
            if extracted:
                return extracted
        text = value.get('text')
        if text:
            return as_text(text)
        if value.get('error'):
            return str(value['error'])
        structured = value.get('structuredContent') or value.get('structured_content')
        if structured is not None:
            return as_text(structured)
        return json.dumps(value, indent=2, default=str)
    text = getattr(value, 'text', None)
    if text:
        return text
    parts = getattr(value, 'parts', None)
    if parts:
        return ''.join(part.text or '' for part in parts)
    content = getattr(value, 'content', None)
    if content is not None and content is not value:
        return as_text(content)
    if hasattr(value, 'model_dump'):
        return as_text(value.model_dump())
    try:
        return json.dumps(value, indent=2, default=str)
    except TypeError:
        return str(value)

def pages_as_markdown(value: object) -> str:
    text = _inner_tool_text(value)
    if text.startswith('Failed to'):
        return text
    lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r'^(\d+):\s+(\S+)', line.strip())
        if match:
            lines.append(f'- `{match.group(1)}`: {match.group(2)}')
    if lines:
        return '\n'.join(lines)
    return _fields_as_markdown(_json_records(text, 'pages'), 'id', 'url')

def webmcp_tools_as_markdown(value: object) -> str:
    text = _inner_tool_text(value)
    if text.startswith('Failed to'):
        return text
    lines: list[str] = []
    for line in text.splitlines():
        name = re.search(r'\bname="([^"]*)"', line)
        if not name:
            continue
        description = re.search(r'\bdescription="([^"]*)"', line)
        item = f'- **{name.group(1)}**'
        if description and description.group(1):
            item += f': {description.group(1)}'
        lines.append(item)
    if lines:
        return '\n'.join(lines)
    return _fields_as_markdown(
        _json_records(text, 'webmcpTools', 'webmcp_tools', 'tools'),
        'name',
        'description',
    )

def _inner_tool_text(value: object) -> str:
    text = as_text(value)
    stripped = text.strip()
    if stripped[:1] not in '{[':
        return text
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return text
    inner = as_text(parsed)
    return inner or text

def _json_records(text: str, *keys: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    structured = data.get('structuredContent') or data.get('structured_content')
    if isinstance(structured, dict):
        data = structured
    for key in keys:
        items = data.get(key)
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    return []

def _fields_as_markdown(records: list[dict[str, Any]], left_key: str, right_key: str) -> str:
    lines: list[str] = []
    for item in records:
        left = item.get(left_key, item.get('pageId') if left_key == 'id' else None)
        right = item.get(right_key)
        if left is None and not right:
            continue
        if left_key == 'id':
            lines.append(f'- `{left}`: {right}')
        else:
            lines.append(f'- **{left}**' + (f': {right}' if right else ''))
    return '\n'.join(lines) or '(none)'

def user_text(value: object) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ('text', 'user_response', 'response', 'message'):
            if value.get(key) is not None:
                return str(value[key])
        return json.dumps(value)
    return as_text(value)

def resume_user_text(ctx: Context) -> str:
    replies = list(ctx.resume_inputs.values())
    first_reply = replies[0]
    return user_text(first_reply)

def as_dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    text = user_text(value)
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}

def tool_input_json(value: object) -> str:
    if value is None or value == '':
        return '{}'
    if isinstance(value, dict):
        return json.dumps(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return '{}'
        return json.dumps(parsed) if isinstance(parsed, dict) else '{}'
    return '{}'

async def run_chrome_devtools_mcp_client_tool(ctx: Context, tool_name: str, args: dict[str, Any] | None = None) -> Any:
    tools: list[Any] = await chrome_devtools_mcp_client.get_tools()
    tool: Any = next((item for item in tools if item.name == tool_name), None)
    if tool is None:
        available: list[str] = [item.name for item in tools]
        raise ValueError(
            f'Chrome DevTools tool "{tool_name}" not found. Available: {available}'
        )
    return await tool.run_async(args=args or {}, tool_context=ctx)

async def refresh_pages(ctx: Context) -> str:
    try:
        pages = await run_chrome_devtools_mcp_client_tool(ctx, 'list_pages')
        ctx.state[STATE_PAGES] = as_text(pages)
    except Exception as error:
        ctx.state[STATE_PAGES] = f'Failed to list pages: {error}'
    return ctx.state[STATE_PAGES]

async def refresh_webmcp_tools(ctx: Context) -> str:
    try:
        tools = await run_chrome_devtools_mcp_client_tool(ctx, 'list_webmcp_tools')
        ctx.state[STATE_WEBMCP_TOOLS] = as_text(tools)
    except Exception as error:
        ctx.state[STATE_WEBMCP_TOOLS] = (
            f'Failed to list WebMCP tools (no selected page, or the page exposes none): {error}'
        )
    return ctx.state[STATE_WEBMCP_TOOLS]

def create_restart_text(reason: object) -> str | None:
    prompts: dict[RestartReason, str] = {
        RestartReason.CHOSE_WRONG: (
            'That input did not match an open-page URL, an existing page, '
            'or a known WebMCP tool. Try again.'
        ),
        RestartReason.PAGE_INVALID: 'The previous page is no longer valid. Open or select a page.',
        RestartReason.ANOTHER_PAGE: 'Switching pages. Open a URL or select an existing page.',
        RestartReason.UNKNOWN: 'Something went wrong. Start over by opening or selecting a page.',
    }
    try:
        return prompts[RestartReason(reason)]
    except ValueError:
        return None
