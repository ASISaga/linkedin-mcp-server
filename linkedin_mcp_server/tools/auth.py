# linkedin_mcp_server/tools/auth.py
"""
LinkedIn authentication and server-management MCP tools.

Registers OAuth lifecycle tools and server information onto a FastMCP instance.
These tools are LinkedIn-specific but follow the same registrar pattern as
the other tool modules so they can be included via mcp_platform.server.
"""

import logging
from typing import Any, Dict

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_auth_tools(mcp: FastMCP) -> None:
    """
    Register authentication and server-management tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance to register tools on.
    """

    @mcp.tool()
    async def get_authentication_status() -> Dict[str, Any]:
        """Get current LinkedIn API authentication status."""
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager

            oauth_manager = get_oauth_manager()
            is_authenticated = oauth_manager.is_authenticated()

            if is_authenticated:
                token_info = oauth_manager.introspect_token()
                return {
                    "status": "authenticated",
                    "token_info": token_info,
                    "message": "Successfully authenticated with LinkedIn API",
                }
            return {
                "status": "not_authenticated",
                "message": "Not authenticated with LinkedIn API",
                "help": "Use get_oauth_authorization_url to begin authentication flow",
            }

        except Exception as e:
            logger.error("Error checking authentication status: %s", e)
            return {
                "status": "error",
                "message": f"Failed to check authentication status: {e}",
            }

    @mcp.tool()
    async def refresh_access_token() -> Dict[str, Any]:
        """Refresh the current access token using the stored refresh token."""
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager

            oauth_manager = get_oauth_manager()
            token_data = oauth_manager.refresh_access_token()
            return {
                "status": "success",
                "message": "Access token refreshed successfully",
                "token_data": token_data,
            }

        except Exception as e:
            logger.error("Error refreshing access token: %s", e)
            return {
                "status": "error",
                "message": f"Failed to refresh access token: {e}",
            }

    @mcp.tool()
    async def get_api_info() -> Dict[str, Any]:
        """
        Get information about the LinkedIn MCP Server API capabilities,
        limitations, and required setup.
        """
        return {
            "api_type": "official_linkedin_api",
            "authentication": "oauth_2_0",
            "capabilities": {
                "profile_access": "Authenticated user's profile only",
                "email_access": "Authenticated user's email (requires 'email' scope)",
                "company_access": "Companies you manage only",
                "job_access": "Your company's job postings only",
                "social_actions": (
                    "Reactions, comments, UGC posts (requires 'w_member_social')"
                ),
                "public_search": "Not available through official API",
            },
            "benefits": {
                "compliance": "Fully compliant with LinkedIn Terms of Service",
                "reliability": "Stable API contract, no scraping fragility",
                "security": "Proper OAuth 2.0 authentication flow",
            },
            "setup_required": {
                "developer_app": "Create LinkedIn Developer Application",
                "api_permissions": "Request appropriate API product access",
                "oauth_setup": "Configure OAuth 2.0 credentials",
                "documentation": "See LINKEDIN_PERMISSIONS_SETUP.md",
            },
        }
