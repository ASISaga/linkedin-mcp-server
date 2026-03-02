# mcp_platform/server.py
"""
Platform-agnostic MCP server factory.

Provides a reusable FastMCP server creation pattern that any social media
platform integration (LinkedIn, Reddit, Twitter, etc.) can use by supplying
its own tool-registrar callables.

Design
------
The factory accepts a list of *registrar* functions.  Each registrar takes a
``FastMCP`` instance and calls ``@mcp.tool()`` on its own tools, following
the same pattern already used in ``linkedin_mcp_server/tools/``.  This keeps
the LinkedIn, Reddit, or any other platform logic entirely separate from the
MCP hosting layer.

Example – hypothetical Reddit adapter::

    # reddit_mcp_server/server.py
    from mcp_platform.server import create_mcp_server
    from reddit_mcp_server.tools.posts import register_post_tools
    from reddit_mcp_server.tools.search import register_search_tools

    def create_reddit_mcp_server() -> FastMCP:
        return create_mcp_server(
            "reddit_api_client",
            [register_post_tools, register_search_tools],
        )
"""

from __future__ import annotations

import logging
from typing import Callable, List

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_mcp_server(
    name: str,
    tool_registrars: List[Callable[[FastMCP], None]],
) -> FastMCP:
    """
    Create a FastMCP server and register tools from all provided registrars.

    This factory is completely platform-agnostic: pass in any combination of
    tool-registrar functions (LinkedIn, Reddit, …) to produce a configured
    MCP server ready to be hosted anywhere (Azure Functions, local stdio, etc.).

    Args:
        name: Server name exposed in the MCP ``initialize`` response
              (e.g. ``"linkedin_api_client"`` or ``"reddit_api_client"``).
        tool_registrars: Ordered list of callables.  Each callable receives the
                         ``FastMCP`` instance and registers its tools on it via
                         ``@mcp.tool()`` decorators.

    Returns:
        FastMCP: Configured server instance with all tools registered.

    Raises:
        ValueError: If ``tool_registrars`` is empty (nothing to serve).
    """
    if not tool_registrars:
        raise ValueError(
            "tool_registrars must contain at least one registrar function."
        )

    mcp = FastMCP(name)

    for register in tool_registrars:
        register(mcp)
        logger.debug("Registered tools from %s", register.__module__)

    logger.info(
        "MCP server '%s' created with %d tool registrar(s).",
        name,
        len(tool_registrars),
    )
    return mcp
