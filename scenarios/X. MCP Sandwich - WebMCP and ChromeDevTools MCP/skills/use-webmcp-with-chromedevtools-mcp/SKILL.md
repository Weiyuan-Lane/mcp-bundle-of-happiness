---
name: use-webmcp-with-chromedevtools-mcp
description: >-
  Use Chrome DevTools MCP to open, list, and select browser pages, then list
  and execute the WebMCP tools those pages expose. Use when the user wants to
  open a URL, switch tabs, navigate to a different page, see available WebMCP
  tools, or run a page-exposed tool.
---

# Use WebMCP through Chrome DevTools MCP

Chrome DevTools MCP is the only way to reach page-exposed WebMCP tools. Those tools are **not** in the agent tool list. Never invent page, tool, or argument names.

## Capabilities

Call only these Chrome DevTools MCP tools for this workflow:

| Goal | Tool | Arguments |
|---|---|---|
| Open a new page | `new_page` | `url` (required) |
| List open pages | `list_pages` | none |
| Select an open page | `select_page` | `pageId` (required), `bringToFront: true` |
| List WebMCP tools on the selected page | `list_webmcp_tools` | none |
| Run a listed WebMCP tool | `execute_webmcp_tool` | `toolName` (exact name), `input` (JSON object string, `{}` if none) |

`list_pages` and `list_webmcp_tools` refresh state. Call both after every open, select, or failed listing.

## Loop

Stay in this loop until the user is done.

1. **Orient.** `list_pages`, then `list_webmcp_tools` on the selected page.
2. **Ask.** Show both lists. Ask what they want to do (see [Prompts](#prompts)).
3. **Act** on exactly one intent:
   - **Open a new page:** they gave a URL → `new_page` → go to step 5.
   - **Select a page:** they picked an already-open page → `select_page` with that `pageId` → go to step 5.
   - **Execute a tool:** they named a tool from the current list → `execute_webmcp_tool` → go to step 5.
   - **Unclear:** do not guess. Re-show the lists and ask again.
4. After `new_page` or `select_page`, the new page is selected. Always re-list its WebMCP tools before offering or running any.
5. **Stay on the page.** Show the current WebMCP tools (and the last tool result, if any). Ask them to name a tool or switch pages.
6. **Validate before execute.** Run `execute_webmcp_tool` only when the name exists in the latest `list_webmcp_tools` result. Pass `input` as a JSON object string that matches that tool's schema (`{}` if it takes no arguments).
7. **Recover.**
   - Unknown tool or bad arguments → say what was wrong, re-show the tool list, ask again.
   - Page gone or tools cannot be listed → `list_pages` and ask them to open or select a page.
   - They want a different page → back to step 1.

Do not call `execute_webmcp_tool` until a page is selected and its tool list is current.

## Prompts

Ask these; do not skip the lists.

**No page yet, or they want to switch pages**

> Current browser pages:
>
> {pages}
>
> WebMCP tools on the selected page:
>
> {tools}
>
> Open a URL, select an existing page, or name a WebMCP tool already on the current page.

**On a selected page**

> WebMCP tools on this page:
>
> {tools}
>
> Name a tool to run, or say you want a different page.

When they ask what they can do, show the WebMCP tool list first. That is how they learn what they can execute.

## Common scenarios

### Open a new page

1. If they gave a working URL, call `new_page` with that `url`.
2. `list_pages` and `list_webmcp_tools`.
3. Show the new page's WebMCP tools and ask which to run.

### Navigate to a different page

Already-open tab:

1. `list_pages`.
2. Ask them to pick a page id if they did not.
3. `select_page` with that `pageId` and `bringToFront: true`.
4. `list_webmcp_tools` and show the new list.

New URL, keep working in a new tab: use **Open a new page**.

### Show WebMCP tools

1. Confirm a page is selected (`list_pages` → `select_page` if needed).
2. `list_webmcp_tools`.
3. Present each tool's **name** and **description**. Offer to run one.

Call `list_webmcp_tools` again after every navigation, tab switch, or reload. The list is per selected page and goes stale.

## Rules

- Use exact `pageId` values from `list_pages` and exact `toolName` values from `list_webmcp_tools`.
- Page WebMCP tools are executed only through `execute_webmcp_tool`. Never treat a page tool as a direct agent tool.
- If a Chrome DevTools call fails, report the error. Do not claim the action succeeded.
- If `list_webmcp_tools` is empty, say the selected page exposes no WebMCP tools. Offer to open or select another page.

