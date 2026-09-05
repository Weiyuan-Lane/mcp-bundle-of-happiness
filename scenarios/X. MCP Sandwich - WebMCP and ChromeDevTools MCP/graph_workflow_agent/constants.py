from enum import StrEnum
from typing import Final

# Context state keys
STATE_PAGES: Final[str] = 'pages'
STATE_WEBMCP_TOOLS: Final[str] = 'webmcp_tools'

# Restart reasons passed to browser_interaction_action via node_input
class RestartReason(StrEnum):
    CHOSE_WRONG = 'chose_wrong'
    PAGE_INVALID = 'page_invalid'
    ANOTHER_PAGE = 'another_page'
    UNKNOWN = 'unknown'
