# linkedin_mcp_server/server.py
"""
LinkedIn MCP server assembly.

Wires together the platform-agnostic MCP factory (mcp_platform.server) with
all LinkedIn-specific tool registrars to produce a ready-to-run FastMCP server.

Separation of concerns
----------------------
- ``mcp_platform.server``        – generic factory, reusable for any platform
- ``linkedin_mcp_server.tools.*`` – LinkedIn-specific tool implementations
- ``azure/function_app.py``      – Azure Functions hosting layer
"""

import logging

from fastmcp import FastMCP

from mcp_platform.server import create_mcp_server
from linkedin_mcp_server.tools.auth import register_auth_tools
from linkedin_mcp_server.tools.company import register_company_tools
from linkedin_mcp_server.tools.job import register_job_tools
from linkedin_mcp_server.tools.person import register_person_tools
from linkedin_mcp_server.tools.social import register_social_tools

logger = logging.getLogger(__name__)

#: Ordered list of tool registrars for the LinkedIn MCP server.
#: Add or remove registrars here to include/exclude capability groups.
_LINKEDIN_TOOL_REGISTRARS = [
    register_person_tools,
    register_company_tools,
    register_job_tools,
    register_social_tools,
    register_auth_tools,
]


def create_linkedin_mcp_server() -> FastMCP:
    """
    Create a fully configured LinkedIn MCP server.

    Uses the platform-agnostic ``mcp_platform.server.create_mcp_server``
    factory with all LinkedIn tool registrars.

    Returns:
        FastMCP: Server instance with all LinkedIn tools registered.
    """
    return create_mcp_server("linkedin_api_client", _LINKEDIN_TOOL_REGISTRARS)


def shutdown_handler() -> None:
    """Clean up resources on shutdown (no-op for the official API path)."""
    pass
