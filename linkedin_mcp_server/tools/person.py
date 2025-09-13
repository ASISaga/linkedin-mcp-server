# src/linkedin_mcp_server/tools/person.py
"""
LinkedIn person profile tools using official LinkedIn API.

Provides MCP tools for extracting LinkedIn profile information through
the official LinkedIn API with OAuth 2.0 authentication.
"""

import logging
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from linkedin_mcp_server.linkedin_auth import get_authenticated_client, get_access_token
from linkedin_mcp_server.exceptions import AuthenticationError, APIError

logger = logging.getLogger(__name__)


def register_person_tools(mcp: FastMCP) -> None:
    """
    Register all person-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool()
    async def get_current_user_profile(fields: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current authenticated user's LinkedIn profile.
        
        Note: This uses the official LinkedIn API which only allows access to 
        the authenticated user's own profile, not arbitrary public profiles.

        Args:
            fields (str, optional): Comma-separated list of fields to retrieve.
                                   Defaults to basic profile information.
                                   Example: "id,firstName,lastName,profilePicture"

        Returns:
            Dict[str, Any]: User profile data
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            # Default fields if none specified
            if not fields:
                fields = "id,firstName,lastName,headline,summary"
            
            query_params = {"fields": fields} if fields else None
            
            logger.info("Fetching current user profile via LinkedIn API")
            response = client.get(
                resource_path="/me",
                access_token=access_token,
                query_params=query_params
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            profile_data = response.entity
            
            # Structure the response for consistency
            structured_data = {
                "id": profile_data.get("id"),
                "first_name": _extract_localized_field(profile_data.get("firstName")),
                "last_name": _extract_localized_field(profile_data.get("lastName")),
                "headline": profile_data.get("headline"),
                "summary": profile_data.get("summary"),
                "profile_picture": profile_data.get("profilePicture"),
                "raw_data": profile_data  # Include full raw response
            }
            
            return structured_data
            
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "error": "Authentication required",
                "message": str(e),
                "help": "Please ensure you have completed the OAuth flow and have a valid access token"
            }
        except APIError as e:
            logger.error(f"LinkedIn API error: {e}")
            return {
                "error": "API request failed",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_current_user_profile: {e}")
            return {
                "error": "Unexpected error",
                "message": str(e)
            }

    @mcp.tool()
    async def get_user_profile_with_openid(projection: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user profile information using OpenID Connect endpoint.
        
        This endpoint provides basic profile information and requires 
        'openid' and 'profile' scopes.

        Args:
            projection (str, optional): Field projection for the response.
                                       Example: "(id,firstName,lastName,picture)"

        Returns:
            Dict[str, Any]: OpenID profile data
        """
        try:
            client = get_authenticated_client()
            access_token = get_access_token()
            
            query_params = {}
            if projection:
                query_params["projection"] = projection
            
            logger.info("Fetching user profile via OpenID Connect")
            response = client.get(
                resource_path="/userinfo",
                access_token=access_token,
                query_params=query_params if query_params else None
            )
            
            if response.status_code != 200:
                raise APIError(f"LinkedIn API returned status {response.status_code}")
            
            return {
                "profile": response.entity,
                "source": "openid_connect"
            }
            
        except Exception as e:
            logger.error(f"Error in get_user_profile_with_openid: {e}")
            return {
                "error": "Failed to fetch OpenID profile",
                "message": str(e)
            }

    @mcp.tool()
    async def get_oauth_authorization_url(scopes: List[str], state: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate OAuth authorization URL for LinkedIn authentication.
        
        Use this to get the URL where users should be redirected to authorize your app.

        Args:
            scopes (List[str]): List of OAuth scopes to request.
                               Common scopes: ['openid', 'profile', 'email', 'w_member_social']
            state (str, optional): State parameter for CSRF protection

        Returns:
            Dict[str, Any]: Authorization URL and metadata
        """
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager
            
            oauth_manager = get_oauth_manager()
            auth_url = oauth_manager.get_authorization_url(scopes, state)
            
            return {
                "authorization_url": auth_url,
                "scopes": scopes,
                "state": state,
                "instructions": "Redirect users to this URL to begin OAuth flow"
            }
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            return {
                "error": "Failed to generate authorization URL",
                "message": str(e)
            }

    @mcp.tool()
    async def exchange_oauth_code(authorization_code: str) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access token.
        
        Call this after user authorizes your app and you receive the authorization code.

        Args:
            authorization_code (str): Authorization code from OAuth callback

        Returns:
            Dict[str, Any]: Access token and metadata
        """
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager
            
            oauth_manager = get_oauth_manager()
            token_data = oauth_manager.exchange_code_for_token(authorization_code)
            
            return {
                "success": True,
                "token_data": token_data,
                "message": "Successfully obtained access token"
            }
            
        except Exception as e:
            logger.error(f"Error exchanging authorization code: {e}")
            return {
                "error": "Failed to exchange authorization code",
                "message": str(e)
            }

    @mcp.tool()
    async def get_token_info() -> Dict[str, Any]:
        """
        Get information about the current access token.

        Returns:
            Dict[str, Any]: Token status and metadata
        """
        try:
            from linkedin_mcp_server.linkedin_auth import get_oauth_manager
            
            oauth_manager = get_oauth_manager()
            token_info = oauth_manager.introspect_token()
            
            return {
                "token_info": token_info,
                "authenticated": oauth_manager.is_authenticated()
            }
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return {
                "error": "Failed to get token information",
                "message": str(e),
                "authenticated": False
            }


def _extract_localized_field(field_data: Any) -> Optional[str]:
    """
    Extract localized field value from LinkedIn API response.
    
    LinkedIn API often returns localized fields in a nested structure.
    
    Args:
        field_data: Field data from API response
        
    Returns:
        Extracted string value or None
    """
    if not field_data:
        return None
    
    if isinstance(field_data, str):
        return field_data
    
    if isinstance(field_data, dict):
        # Handle localized field structure
        localized = field_data.get("localized", {})
        if localized:
            # Return first available localized value
            for locale, value in localized.items():
                if value:
                    return value
        
        # Fallback to preferredLocale if available
        preferred_locale = field_data.get("preferredLocale", {})
        if preferred_locale:
            locale_key = f"{preferred_locale.get('language', 'en')}_{preferred_locale.get('country', 'US')}"
            return localized.get(locale_key)
    
    return str(field_data) if field_data else None
