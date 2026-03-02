# linkedin_mcp_server/__init__.py
"""
LinkedIn MCP Server package.

A Model Context Protocol (MCP) server that provides LinkedIn integration
capabilities using the official LinkedIn REST API with OAuth 2.0 authentication.

Architecture (modular, reusable layers):
- mcp_platform/  : platform-agnostic MCP server factory (reusable for Reddit, etc.)
- linkedin_mcp_server/ : LinkedIn-specific tools and authentication
- azure/         : Azure Functions hosting (HTTP + Service Bus triggers)
- azure/bicep/   : Bicep IaC for Flexible Consumption plan provisioning
"""

__version__ = "0.1.0"
