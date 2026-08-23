import os
import uuid
from typing import Literal
from google.adk import Agent, Context, Event, Workflow
from google.adk.events import RequestInput
from google.adk.workflow import DEFAULT_ROUTE, FunctionNode
from pydantic import BaseModel
from dotenv import load_dotenv
from .constants import (
    RESTART_ANOTHER_PAGE,
    RESTART_CHOSE_WRONG,
    RESTART_PAGE_INVALID,
    RESTART_UNKNOWN,
    STATE_PAGES,
    STATE_WEBMCP_TOOLS,
)
from .utils import as_dict, as_text, pages_as_markdown, webmcp_tools_as_markdown, run_chrome_devtools_mcp_client_tool, refresh_pages, refresh_webmcp_tools, create_restart_text, resume_user_text, tool_input_json
load_dotenv()

# Get environment variables ---------------------------------------------------
MODEL_VERSION = os.getenv('SCENARIO_X_MODEL_VERSION')
# end -------------------------------------------------------------------------

class BrowserInteractionDecision(BaseModel):
    intent: Literal[
        'open_page',
        'select_page',
        'execute_webmcp_tool',
        'browser_interaction_from_start',
    ]
    url: str | None = None
    page_id: int | None = None
    tool_name: str | None = None
    tool_input: str | None = None
    reason: str | None = None

class WebmcpValidationDecision(BaseModel):
    decision: Literal[
        'execute_webmcp_tool',
        'invalid_webmcp_tool',
        'page_invalid',
        'another_page',
        'unknown',
    ]
    tool_name: str | None = None
    tool_input: str | None = None
    reason: str | None = None


# Graph Chrome DevTools MCP client flow - Declare deps first ------------------
async def browser_interaction_action(ctx: Context, node_input):
    # If this was passed from a resume, get the user reply and refresh the pages and webmcp tools
    if ctx.resume_inputs:
        user_reply = resume_user_text(ctx)
        await refresh_pages(ctx)
        await refresh_webmcp_tools(ctx)
        yield Event(output = user_reply)
        return

    # START already has the first user message — skip the prompt and classify it.
    if not isinstance(node_input, dict):
        await refresh_pages(ctx)
        await refresh_webmcp_tools(ctx)
        yield Event(output = as_text(node_input))
        return

    # If this was passed from another action node, get the restart reason to display to the user
    restart_reason = as_dict(node_input).get('restart_reason', None)

    # Retrieve states needed to build the message to display to the user
    pages = await refresh_pages(ctx)
    webmcp_tools = await refresh_webmcp_tools(ctx)

    # Build the message to display to the user
    message = (
        f'Current browser pages:\n\n{pages_as_markdown(pages)}\n\n'
        f'WebMCP tools on the selected page:\n\n{webmcp_tools_as_markdown(webmcp_tools)}\n\n'
    )
    restart_text = create_restart_text(restart_reason)
    if restart_text:
        message += f'{restart_text}\n\n'
    message += (
        'What do you want to do? Open a URL, select an existing page, '
        'or name a WebMCP tool already on the current page.'
    )

    yield RequestInput(
        interrupt_id = f'browser-interaction-{uuid.uuid4()}',
        message = message,
    )

browser_interaction_action_node = FunctionNode(
    func = browser_interaction_action,
    name = 'browser_interaction_action_node',
    rerun_on_resume = True,
)

def browser_interaction_instruction(ctx) -> str:
    return (
        'Classify the user request. Use only the current page list and WebMCP tool list.\n\n'
        f'Current pages:\n{pages_as_markdown(ctx.state.get(STATE_PAGES))}\n\n'
        f'WebMCP tools on the selected page:\n{webmcp_tools_as_markdown(ctx.state.get(STATE_WEBMCP_TOOLS))}\n\n'
        'Choose exactly one intent:\n'
        '- open_page: the user gave a working URL to open. Set url.\n'
        '- select_page: the user chose an already-open page. Set page_id from the list.\n'
        '- execute_webmcp_tool: the user named a WebMCP tool that exists in the list '
        'and can be executed now. Set tool_name to that exact name, and tool_input as a '
        'JSON object string (use {} if there are no arguments).\n'
        '- browser_interaction_from_start: none of the above match.\n'
        'Do not invent tool names, URLs, or page ids.'
    )

browser_interaction_agent = Agent(
    model = MODEL_VERSION,
    name = 'browser_interaction_agent',
    instruction = browser_interaction_instruction,
    output_schema = BrowserInteractionDecision,
    mode = 'single_turn',
)

def browser_interaction_router(ctx: Context, node_input):
    payload = as_dict(node_input)
    intent = payload.get('intent')

    if intent == 'open_page' and payload.get('url'):
        output = {'url': payload['url']}
        return Event(output = output, route = 'open_page')

    if intent == 'select_page' and payload.get('page_id') is not None:
        output = {'page_id': payload['page_id']}
        return Event(output = output, route = 'select_page')

    if intent == 'execute_webmcp_tool' and payload.get('tool_name'):
        output = {
            'tool_name': payload['tool_name'],
            'tool_input': tool_input_json(payload.get('tool_input')),
        }
        return Event(output = output, route = 'execute_webmcp_tool')

    output = {'restart_reason': RESTART_CHOSE_WRONG}
    return Event(output = output, route = 'browser_interaction_from_start')

async def open_page_action_and_router_node(ctx: Context, node_input):
    url = as_dict(node_input).get('url', None)
    if not url:
        output = {'error': 'missing url', 'restart_reason': RESTART_UNKNOWN}
        return Event(
            message = 'No URL was provided to open.',
            output = output,
            route = 'browser_interaction_from_start',
        )

    try:
        result = await run_chrome_devtools_mcp_client_tool(ctx, 'new_page', {'url': url})
    except Exception as error:
        output = {'error': str(error), 'restart_reason': RESTART_UNKNOWN}
        return Event(
            message = f'Failed to open {url}: {error}',
            output = output,
            route = 'browser_interaction_from_start',
        )

    await refresh_pages(ctx)
    output = {'url': url, 'result': as_text(result)}
    return Event(
        message = f'Opened {url}',
        output = output,
        route = 'interact_with_webmcp_tool',
    )

async def select_page_action_and_router_node(ctx: Context, node_input):
    page_id = as_dict(node_input).get('page_id', None)
    if page_id is None:
        output = {'error': 'missing page_id', 'restart_reason': RESTART_UNKNOWN}
        return Event(
            message = 'No page id was provided to select.',
            output = output,
            route = 'browser_interaction_from_start',
        )

    try:
        result = await run_chrome_devtools_mcp_client_tool(
            ctx,
            'select_page',
            {'pageId': int(page_id), 'bringToFront': True},
        )
    except Exception as error:
        output = {'error': str(error), 'restart_reason': RESTART_UNKNOWN}
        return Event(
            message = f'Failed to select page {page_id}: {error}',
            output = output,
            route = 'browser_interaction_from_start',
        )

    await refresh_pages(ctx)
    output = {'page_id': page_id, 'result': as_text(result)}
    return Event(
        message = f'Selected page {page_id}',
        output = output,
        route = 'interact_with_webmcp_tool',
    )

async def interact_with_webmcp_tool_action(ctx: Context, node_input):
    if ctx.resume_inputs:
        user_reply = resume_user_text(ctx)
        await refresh_webmcp_tools(ctx)
        yield Event(output = user_reply)
        return

    outcome_message = as_dict(node_input).get('outcome_message', None)

    webmcp_tools = await refresh_webmcp_tools(ctx)
    message = f'WebMCP tools on this page:\n\n{webmcp_tools_as_markdown(webmcp_tools)}\n\n'
    if outcome_message:
        message = f'{outcome_message}\n\n{message}'
    message += 'Name a tool to run, or say you want a different page.'

    yield RequestInput(
        interrupt_id = f'webmcp-tool-{uuid.uuid4()}',
        message = message,
    )

interact_with_webmcp_tool_action_node = FunctionNode(
    func=interact_with_webmcp_tool_action,
    name='interact_with_webmcp_tool_action_node',
    rerun_on_resume=True,
)

def validate_webmcp_instruction(ctx) -> str:
    return (
        'Validate whether the user wants to run a WebMCP tool on the current page.\n\n'
        f'Known WebMCP tools:\n{webmcp_tools_as_markdown(ctx.state.get(STATE_WEBMCP_TOOLS))}\n\n'
        'Choose exactly one decision:\n'
        '- execute_webmcp_tool: they named a tool that exists above. Set tool_name to '
        'that exact name, and tool_input as a JSON object string (use {} if none).\n'
        '- invalid_webmcp_tool: they want a tool, but the name or arguments do not match. '
        'Set reason to a short correction prompt.\n'
        '- page_invalid: the page looks gone or tools cannot be listed.\n'
        '- another_page: they want to open or select a different page.\n'
        '- unknown: anything else that should restart from the start.\n'
        'Do not invent tool names.'
    )


validate_and_execute_webmcp_agent = Agent(
    model = MODEL_VERSION,
    name = 'validate_and_execute_webmcp_agent',
    instruction = validate_webmcp_instruction,
    output_schema = WebmcpValidationDecision,
    mode = 'single_turn',
)

def validate_and_execute_webmcp_router(ctx: Context, node_input):
    payload = as_dict(node_input)
    decision = payload.get('decision')

    if decision == 'execute_webmcp_tool' and payload.get('tool_name'):
        output = {
            'tool_name': payload['tool_name'],
            'tool_input': tool_input_json(payload.get('tool_input')),
        }
        return Event(output = output, route = 'execute_webmcp_tool')

    if decision == 'invalid_webmcp_tool':
        output = {
            'outcome_message': payload.get('reason') or (
                'That WebMCP tool is not valid. Describe the tool more clearly using a name from the list.'
            ),
        }
        return Event(output = output, route = 'invalid_webmcp_tool')

    if decision == 'page_invalid':
        restart_reason = RESTART_PAGE_INVALID
    elif decision == 'another_page':
        restart_reason = RESTART_ANOTHER_PAGE
    else:
        restart_reason = RESTART_UNKNOWN
    output = {'restart_reason': restart_reason}
    return Event(output = output, route = 'browser_interaction_from_start')


async def execute_webmcp_tool_action_node(ctx: Context, node_input):
    payload = as_dict(node_input)
    tool_name = payload.get('tool_name', None)
    tool_input = tool_input_json(payload.get('tool_input', None))
    if not tool_name:
        outcome_message = 'No WebMCP tool was selected to execute.'
        return Event(
            message = outcome_message,
            output = {'error': 'missing tool', 'outcome_message': outcome_message},
        )

    try:
        result = await run_chrome_devtools_mcp_client_tool(
            ctx,
            'execute_webmcp_tool',
            {'toolName': tool_name, 'input': tool_input},
        )
    except Exception as error:
        outcome_message = f'Failed to run `{tool_name}`: {error}'
        return Event(
            message = outcome_message,
            output = {'error': str(error), 'outcome_message': outcome_message},
        )

    result_text = as_text(result)
    outcome_message = f'Ran `{tool_name}`'
    return Event(
        message = outcome_message,
        output = {'tool_name': tool_name, 'result': result_text, 'outcome_message': outcome_message},
    )


def invalid_webmcp_tool_action_node(ctx: Context, node_input):
    outcome_message = as_dict(node_input).get('outcome_message', None)
    if not outcome_message:
        outcome_message = (
            'The last WebMCP tool request was invalid. '
            'Describe the tool more clearly using a name from the list.'
        )
    output = {'outcome_message': outcome_message}
    return Event(message = outcome_message, output = output)

# end -------------------------------------------------------------------------


# Graph workflow agent flow - Edges and workflows -----------------------------
# Tip -
#   (1) Start a flow or branch with an "action" node (whether to yield response or gather data or perform an action)
#   (2) Next, proceed to the "agent" node to parse and decide on next action
#   (3) Finally, optionally a "router" node to branch OR to another "action" node
#   (4) If "router", use it to branch to more "action" nodes
#   Since most action nodes are the start of the flow, the flow repeats and this is easier to plan and visualise!
#
browser_interaction_edges = [
    # Main browser interaction flow - select page before interacting with webmcp tool
    ('START', browser_interaction_action_node, browser_interaction_agent, browser_interaction_router),
    (browser_interaction_router, {
            'open_page': open_page_action_and_router_node,
            'select_page': select_page_action_and_router_node,
            'execute_webmcp_tool': execute_webmcp_tool_action_node,
            DEFAULT_ROUTE: browser_interaction_action_node,
        }
    ),

    # Once open page, move users to interact with webmcp tool
    (open_page_action_and_router_node, {
        'interact_with_webmcp_tool': interact_with_webmcp_tool_action_node,
        DEFAULT_ROUTE: browser_interaction_action_node,
    }),

    # Once select page, move users to interact with webmcp tool
    (select_page_action_and_router_node, {
        'interact_with_webmcp_tool': interact_with_webmcp_tool_action_node,
        DEFAULT_ROUTE: browser_interaction_action_node,
    }),

    # When interacting with webmcp tool
    #   (1) Yield to get user input
    #   (2) Validate that user wants to execute a tool, or reset the page and start over
    #   (3) Execute the tools, and then loop back to asking for another tool to validate and execute
    (interact_with_webmcp_tool_action_node, validate_and_execute_webmcp_agent, validate_and_execute_webmcp_router),
    (validate_and_execute_webmcp_router,
        {
            'execute_webmcp_tool': execute_webmcp_tool_action_node,
            'invalid_webmcp_tool': invalid_webmcp_tool_action_node,
            DEFAULT_ROUTE: browser_interaction_action_node,
        }
    ),
    (execute_webmcp_tool_action_node, interact_with_webmcp_tool_action_node),
    (invalid_webmcp_tool_action_node, interact_with_webmcp_tool_action_node),
]

root_agent = Workflow(
    name = 'root_agent',
    edges = browser_interaction_edges,
)
# end -------------------------------------------------------------------------
