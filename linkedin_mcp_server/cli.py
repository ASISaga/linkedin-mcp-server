# src/linkedin_mcp_server/cli.py
"""
CLI utilities for LinkedIn MCP server configuration generation with OAuth support.

Generates Claude Desktop configuration for the official LinkedIn API with OAuth 2.0
authentication, environment variables, and clipboard integration for setup workflow.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, List

import pyperclip  # type: ignore

from linkedin_mcp_server.config import get_config

logger = logging.getLogger(__name__)


def print_claude_config() -> None:
    """
    Print Claude configuration for official LinkedIn API and copy to clipboard.

    This function generates the configuration needed for Claude Desktop
    with OAuth 2.0 authentication setup.
    """
    config = get_config()
    current_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Find the full path to uv executable
    try:
        uv_path = subprocess.check_output(["which", "uv"], text=True).strip()
        print(f"🔍 Found uv at: {uv_path}")
    except subprocess.CalledProcessError:
        # Fallback if which uv fails
        uv_path = "uv"
        print(
            "⚠️ Could not find full path to uv, using 'uv' directly. "
            "This may not work in Claude Desktop."
        )

    # Command-line arguments for official API
    args: List[str] = [
        "--directory",
        current_dir,
        "run",
        "-m",
        "linkedin_mcp_server",
    ]

    # Environment variables for OAuth configuration
    env_vars: Dict[str, str] = {}
    
    # OAuth credentials
    if config.linkedin.client_id:
        env_vars["LINKEDIN_CLIENT_ID"] = config.linkedin.client_id
    else:
        env_vars["LINKEDIN_CLIENT_ID"] = "your_client_id_here"
        
    if config.linkedin.client_secret:
        env_vars["LINKEDIN_CLIENT_SECRET"] = config.linkedin.client_secret
    else:
        env_vars["LINKEDIN_CLIENT_SECRET"] = "your_client_secret_here"
        
    if config.linkedin.redirect_uri:
        env_vars["LINKEDIN_REDIRECT_URI"] = config.linkedin.redirect_uri
    
    # Optional: Direct access token
    if config.linkedin.access_token:
        env_vars["LINKEDIN_ACCESS_TOKEN"] = config.linkedin.access_token
    else:
        env_vars["LINKEDIN_ACCESS_TOKEN"] = "optional_direct_access_token"

    # Updated tool list for official API
    required_tools = [
        "get_current_user_profile",
        "get_oauth_authorization_url",
        "exchange_oauth_code",
        "get_token_info",
        "search_companies",
        "get_managed_companies",
        "search_job_postings",
        "get_authentication_status"
    ]

    config_json: Dict[str, Any] = {
        "mcpServers": {
            "linkedin-api": {
                "command": uv_path,
                "args": args,
                "env": env_vars,
                "disabled": False,
                "requiredTools": required_tools,
            }
        }
    }

    # Convert to string for clipboard
    config_str = json.dumps(config_json, indent=2)

    # Print the final configuration
    print("\n📋 Your Claude configuration for LinkedIn Official API:")
    print(config_str)
    print("\n🔧 Setup Instructions:")
    print("1. Add this to your Claude Desktop configuration in Settings > Developer > Edit Config")
    print("2. Replace 'your_client_id_here' and 'your_client_secret_here' with your actual LinkedIn OAuth credentials")
    print("3. See LINKEDIN_PERMISSIONS_SETUP.md for detailed setup instructions")
    print("4. Use get_oauth_authorization_url tool to begin authentication flow")

    # Copy to clipboard
    try:
        pyperclip.copy(config_str)
        print("✅ Claude configuration copied to clipboard!")
    except ImportError:
        print(
            "⚠️ pyperclip not installed. To copy configuration automatically, run: pip install pyperclip"
        )
    except Exception as e:
        print(f"❌ Could not copy to clipboard: {e}")


def print_oauth_setup_info() -> None:
    """
    Print OAuth setup information and instructions.
    """
    print("\n🔐 LinkedIn OAuth 2.0 Setup Guide")
    print("=" * 50)
    print("\n1. Create LinkedIn Developer App:")
    print("   - Go to https://www.linkedin.com/developers/apps/")
    print("   - Click 'Create App'")
    print("   - Fill in required information")
    print("   - Note your Client ID and Client Secret")
    
    print("\n2. Configure OAuth Settings:")
    print("   - Add redirect URL: http://localhost:8000/auth/callback")
    print("   - Request API product access (Sign In with LinkedIn, etc.)")
    
    print("\n3. Set Environment Variables:")
    print("   export LINKEDIN_CLIENT_ID='your_client_id'")
    print("   export LINKEDIN_CLIENT_SECRET='your_client_secret'")
    print("   export LINKEDIN_REDIRECT_URI='http://localhost:8000/auth/callback'")
    
    print("\n4. OAuth Flow:")
    print("   - Use get_oauth_authorization_url to get authorization URL")
    print("   - Direct user to authorization URL")
    print("   - Get authorization code from callback")
    print("   - Use exchange_oauth_code to get access token")
    
    print("\n📖 For detailed instructions, see: LINKEDIN_PERMISSIONS_SETUP.md")


def print_api_migration_info() -> None:
    """
    Print information about the migration from scraping to official API.
    """
    print("\n🔄 LinkedIn API Migration Information")
    print("=" * 50)
    print("\n✅ Migration Completed:")
    print("   - Web scraping → Official LinkedIn API")
    print("   - Cookie authentication → OAuth 2.0")
    print("   - Chrome/Selenium → REST API client")
    print("   - Terms violation → Compliant API usage")
    
    print("\n⚠️ Key Limitations:")
    print("   - Profile access: Only authenticated user's profile")
    print("   - Company access: Only companies you manage")
    print("   - Job access: Only your company's job postings")
    print("   - No public profile/company search")
    
    print("\n🎯 Available Features:")
    print("   - User profile information (with proper scopes)")
    print("   - Company management (with admin permissions)")
    print("   - Job posting management (with admin permissions)")
    print("   - OAuth 2.0 authentication flow")
    
    print("\n📋 Required Setup:")
    print("   1. LinkedIn Developer Application")
    print("   2. OAuth 2.0 credentials configuration")
    print("   3. API product permissions")
    print("   4. User authorization flow")
