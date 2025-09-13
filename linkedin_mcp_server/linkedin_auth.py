# linkedin_mcp_server/linkedin_auth.py
"""
LinkedIn OAuth 2.0 authentication management for official LinkedIn API.

Handles OAuth 2.0 flow, token management, and provides authenticated clients
for LinkedIn API interactions.
"""

import logging
import os
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from linkedin_api.clients.auth.client import AuthClient
from linkedin_api.clients.restli.client import RestliClient

from linkedin_mcp_server.config import get_config
from linkedin_mcp_server.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class LinkedInOAuthManager:
    """
    Manages LinkedIn OAuth 2.0 authentication and provides authenticated API clients.
    """
    
    def __init__(self):
        """Initialize OAuth manager with configuration."""
        self.config = get_config()
        
        # OAuth credentials from environment
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/auth/callback')
        
        if not self.client_id or not self.client_secret:
            raise AuthenticationError(
                "LinkedIn OAuth credentials not found. Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables."
            )
        
        # Initialize OAuth client
        self.auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_url=self.redirect_uri
        )
        
        # Access token storage
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None
        
        # Try to load existing access token from environment
        existing_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        if existing_token:
            self._access_token = existing_token
            logger.info("Using existing access token from environment")

    def get_authorization_url(self, scopes: list[str], state: Optional[str] = None) -> str:
        """
        Generate authorization URL to redirect users for OAuth consent.
        
        Args:
            scopes: List of OAuth scopes to request
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL string
        """
        try:
            auth_url = self.auth_client.generate_member_auth_url(scopes, state)
            logger.info(f"Generated authorization URL for scopes: {', '.join(scopes)}")
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {e}")
            raise AuthenticationError(f"Failed to generate authorization URL: {e}")

    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Token response containing access token and metadata
        """
        try:
            response = self.auth_client.exchange_auth_code_for_access_token(authorization_code)
            
            # Store token information
            self._access_token = response.access_token
            self._refresh_token = getattr(response, 'refresh_token', None)
            self._token_expires_at = getattr(response, 'expires_in', None)
            
            logger.info("Successfully exchanged authorization code for access token")
            
            return {
                'access_token': response.access_token,
                'expires_in': getattr(response, 'expires_in', None),
                'refresh_token': getattr(response, 'refresh_token', None),
                'scope': getattr(response, 'scope', None)
            }
        except Exception as e:
            logger.error(f"Failed to exchange authorization code: {e}")
            raise AuthenticationError(f"Failed to exchange authorization code: {e}")

    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Returns:
            New token response
        """
        if not self._refresh_token:
            raise AuthenticationError("No refresh token available")
        
        try:
            response = self.auth_client.exchange_refresh_token_for_access_token(self._refresh_token)
            
            # Update stored tokens
            self._access_token = response.access_token
            if hasattr(response, 'refresh_token'):
                self._refresh_token = response.refresh_token
            
            logger.info("Successfully refreshed access token")
            
            return {
                'access_token': response.access_token,
                'expires_in': getattr(response, 'expires_in', None),
                'refresh_token': getattr(response, 'refresh_token', None)
            }
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise AuthenticationError(f"Failed to refresh access token: {e}")

    def get_access_token(self) -> str:
        """
        Get current access token.
        
        Returns:
            Current access token
            
        Raises:
            AuthenticationError: If no access token is available
        """
        if not self._access_token:
            raise AuthenticationError(
                "No access token available. Please complete OAuth flow or set LINKEDIN_ACCESS_TOKEN environment variable."
            )
        return self._access_token

    def get_restli_client(self) -> RestliClient:
        """
        Get authenticated Rest.li API client.
        
        Returns:
            Configured RestliClient instance
        """
        return RestliClient()

    def introspect_token(self) -> Dict[str, Any]:
        """
        Introspect current access token to get information about its status and scopes.
        
        Returns:
            Token introspection response
        """
        try:
            token = self.get_access_token()
            response = self.auth_client.introspect_access_token(token)
            
            return {
                'active': response.active,
                'auth_type': getattr(response, 'auth_type', None),
                'client_id': getattr(response, 'client_id', None),
                'expires_at': getattr(response, 'expires_at', None),
                'scope': getattr(response, 'scope', None),
                'status': getattr(response, 'status', None)
            }
        except Exception as e:
            logger.error(f"Failed to introspect token: {e}")
            raise AuthenticationError(f"Failed to introspect token: {e}")

    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        try:
            token_info = self.introspect_token()
            return token_info.get('active', False) and token_info.get('status') == 'active'
        except:
            return False


# Global OAuth manager instance
_oauth_manager = None


def get_oauth_manager() -> LinkedInOAuthManager:
    """
    Get or create global OAuth manager instance.
    
    Returns:
        LinkedInOAuthManager instance
    """
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = LinkedInOAuthManager()
    return _oauth_manager


def get_authenticated_client() -> RestliClient:
    """
    Get authenticated LinkedIn API client.
    
    Returns:
        Configured RestliClient instance
        
    Raises:
        AuthenticationError: If not authenticated
    """
    oauth_manager = get_oauth_manager()
    return oauth_manager.get_restli_client()


def get_access_token() -> str:
    """
    Get current access token.
    
    Returns:
        Current access token
        
    Raises:
        AuthenticationError: If not authenticated
    """
    oauth_manager = get_oauth_manager()
    return oauth_manager.get_access_token()