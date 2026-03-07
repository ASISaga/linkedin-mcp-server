# mcp_platform/__init__.py
"""
Platform-agnostic MCP server infrastructure.

This package provides the generic MCP server factory and hosting utilities
that any social media integration can use – LinkedIn, Reddit, Twitter, etc.

Usage example for a Reddit MCP server:

    from mcp_platform.server import create_mcp_server
    from reddit_mcp_server.tools import register_all_tools

    def create_reddit_mcp_server():
        return create_mcp_server("reddit_api_client", [register_all_tools])
"""
