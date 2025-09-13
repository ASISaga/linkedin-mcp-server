# src/linkedin_mcp_server/server.py
"""
FastMCP server implementation for LinkedIn integration using official LinkedIn API.

Creates and configures the MCP server with LinkedIn tool suite including
OAuth authentication, profile access, company management, and job tools.
Uses official LinkedIn API instead of web scraping for compliance and reliability.
"""

import logging
from typing import Any, Dict

from fastmcp import FastMCP

from linkedin_mcp_server.tools.company import register_company_tools
from linkedin_mcp_server.tools.job import register_job_tools
from linkedin_mcp_server.tools.person import register_person_tools

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all LinkedIn tools."""
    mcp = FastMCP("linkedin_api_client")

    # Register all tools
    register_person_tools(mcp)
    register_company_tools(mcp)
    register_job_tools(mcp)

    # Register authentication and session management tools
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
                    "message": "Successfully authenticated with LinkedIn API"
                }
            else:
                return {
                    "status": "not_authenticated",
                    "message": "Not authenticated with LinkedIn API",
                    "help": "Use get_oauth_authorization_url to begin authentication flow"
                }
                
        except Exception as e:
            logger.error(f"Error checking authentication status: {e}")
            return {
                "status": "error",
                "message": f"Failed to check authentication status: {str(e)}"
            }

    @mcp.tool()
    async def refresh_access_token() -> Dict[str, Any]:
        """Refresh the current access token using refresh token."""
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager
            
            oauth_manager = get_oauth_manager()
            token_data = oauth_manager.refresh_access_token()
            
            return {
                "status": "success",
                "message": "Access token refreshed successfully",
                "token_data": token_data
            }
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return {
                "status": "error", 
                "message": f"Failed to refresh access token: {str(e)}"
            }

    @mcp.tool()
    async def get_api_migration_info() -> Dict[str, Any]:
        """Get information about the migration from scraping to official LinkedIn API."""
        return {
            "migration_status": "completed",
            "api_type": "official_linkedin_api",
            "authentication": "oauth_2_0",
            "key_changes": {
                "authentication": "Cookie-based → OAuth 2.0 with access tokens",
                "data_access": "Web scraping → Official API endpoints", 
                "setup": "Chrome/Selenium → LinkedIn Developer App configuration",
                "permissions": "Public scraping → Explicit API permissions"
            },
            "capabilities": {
                "profile_access": "Authenticated user's profile only",
                "company_access": "Companies you manage only",
                "job_access": "Your company's job postings only",
                "public_search": "Not available through official API"
            },
            "benefits": {
                "compliance": "Fully compliant with LinkedIn Terms of Service",
                "reliability": "Stable API contract, no breaking changes from UI updates",
                "security": "Proper OAuth 2.0 authentication flow",
                "enterprise_ready": "Suitable for production applications"
            },
            "limitations": {
                "data_coverage": "Much more limited than scraping approach",
                "public_profiles": "Cannot access arbitrary public profiles",
                "job_search": "No public job search capabilities",
                "company_data": "Limited to companies you have permissions for"
            },
            "setup_required": {
                "developer_app": "Create LinkedIn Developer Application",
                "api_permissions": "Request appropriate API product access",
                "oauth_setup": "Configure OAuth 2.0 credentials",
                "documentation": "See LINKEDIN_PERMISSIONS_SETUP.md"
            }
        }

    return mcp


def shutdown_handler() -> None:
    """Clean up resources on shutdown."""
    from linkedin_mcp_server.drivers.chrome import close_all_drivers

    close_all_drivers()
