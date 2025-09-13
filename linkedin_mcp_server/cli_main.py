# linkedin_mcp_server/cli_main.py
"""
LinkedIn MCP Server - Main CLI application entry point using official LinkedIn API.

Implements OAuth 2.0 authentication flow for the official LinkedIn API:
1. Configuration and Logging Setup
2. OAuth Authentication Management  
3. MCP Server Runtime with API client
"""

import io
import logging
import sys
from typing import Literal

try:
    import inquirer  # type: ignore
except ImportError:
    inquirer = None

from linkedin_mcp_server.cli import (
    print_claude_config, 
    print_oauth_setup_info,
    print_api_migration_info
)
from linkedin_mcp_server.config import get_config
from linkedin_mcp_server.exceptions import AuthenticationError, ConfigurationError
from linkedin_mcp_server.logging_config import configure_logging
from linkedin_mcp_server.server import create_mcp_server

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

logger = logging.getLogger(__name__)


def choose_transport_interactive() -> Literal["stdio", "streamable-http"]:
    """Prompt user for transport mode using inquirer."""
    if not inquirer:
        print("Interactive mode requires 'inquirer' package. Using stdio transport.")
        return "stdio"
        
    questions = [
        inquirer.List(
            "transport",
            message="Choose MCP transport mode",
            choices=[
                ("STDIO (for Claude Desktop)", "stdio"),
                ("HTTP (for web-based MCP clients)", "streamable-http"),
            ],
        )
    ]
    answers = inquirer.prompt(questions)
    return answers["transport"] if answers else "stdio"


def show_oauth_setup() -> None:
    """Show OAuth setup information and exit."""
    print_oauth_setup_info()
    sys.exit(0)


def show_migration_info() -> None:
    """Show API migration information and exit."""
    print_api_migration_info()
    sys.exit(0)


def check_oauth_configuration() -> None:
    """
    Check if OAuth configuration is available.
    
    Raises:
        ConfigurationError: If OAuth configuration is missing
    """
    config = get_config()
    
    # Check if we have either OAuth credentials or a direct access token
    has_oauth_creds = bool(config.linkedin.client_id and config.linkedin.client_secret)
    has_access_token = bool(config.linkedin.access_token)
    
    if not has_oauth_creds and not has_access_token:
        raise ConfigurationError(
            "LinkedIn OAuth configuration is missing. You need either:\n"
            "  1. OAuth credentials: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET\n"
            "  2. Direct access token: LINKEDIN_ACCESS_TOKEN\n"
            "\nSee LINKEDIN_PERMISSIONS_SETUP.md for detailed setup instructions."
        )
    
    if has_oauth_creds:
        logger.info("OAuth credentials configured - authentication flow available")
    if has_access_token:
        logger.info("Direct access token configured - API access available")


def test_api_connection() -> None:
    """
    Test connection to LinkedIn API.
    """
    try:
        from linkedin_mcp_server.linkedin_auth import get_oauth_manager
        
        oauth_manager = get_oauth_manager()
        
        # Try to check authentication status
        is_authenticated = oauth_manager.is_authenticated()
        if is_authenticated:
            token_info = oauth_manager.introspect_token()
            logger.info(f"✅ API connection successful - Token active: {token_info.get('active', False)}")
            print("✅ LinkedIn API connection verified")
        else:
            logger.info("OAuth configured but not yet authenticated")
            print("⚠️ OAuth configured but authentication required")
            print("💡 Use get_oauth_authorization_url tool to begin authentication")
            
    except Exception as e:
        logger.warning(f"API connection test failed: {e}")
        print("⚠️ API connection test failed - OAuth flow may be required")


def get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        import os
        import tomllib

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        if os.path.exists(pyproject_path):
            with open(pyproject_path, "rb") as f:
                pyproject = tomllib.load(f)
            return pyproject.get("project", {}).get("version", "unknown")
        else:
            return "development"

    except Exception:
        return "unknown"


def main() -> None:
    """Main application entry point for LinkedIn API MCP server."""
    
    # Get configuration
    config = get_config()

    # Configure logging FIRST
    configure_logging(
        log_level=config.server.log_level,
        json_format=not config.is_interactive and config.server.log_level != "DEBUG",
    )

    # Get version for display
    version = get_version()

    # Only print banner in interactive mode
    if config.is_interactive:
        print(f"🔗 LinkedIn MCP Server (Official API) v{version} 🔗")
        print("=" * 50)

    # Always log version
    logger.info(f"🔗 LinkedIn MCP Server (Official API) v{version} 🔗")

    logger.debug(f"Server configuration: {config}")

    # Phase 1: Check OAuth Configuration
    try:
        check_oauth_configuration()
        if config.is_interactive:
            print("✅ OAuth configuration found")
        logger.info("OAuth configuration validated")
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        if config.is_interactive:
            print(f"\n❌ Configuration Error:")
            print(str(e))
            print("\n💡 See LINKEDIN_PERMISSIONS_SETUP.md for setup instructions")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected configuration error: {e}")
        print(f"\n❌ Configuration failed: {e}")
        sys.exit(1)

    # Phase 2: Test API Connection (optional)
    if config.is_interactive:
        try:
            test_api_connection()
        except Exception as e:
            logger.warning(f"API connection test failed: {e}")
            print(f"⚠️ API connection test failed: {e}")

    # Phase 3: Server Runtime
    try:
        # Decide transport mode
        transport = config.server.transport

        # Show transport prompt in interactive mode if not explicitly set
        if config.is_interactive and not config.server.transport_explicitly_set:
            print("\n🚀 Server ready! Choose transport mode:")
            transport = choose_transport_interactive()

        # Show Claude configuration for stdio transport in interactive mode
        if config.is_interactive and transport == "stdio":
            print_claude_config()

        # Create and run the MCP server
        mcp = create_mcp_server()

        # Start server
        print(f"\n🚀 Running LinkedIn MCP server ({transport.upper()} mode)...")
        print("📱 Available tools: OAuth authentication, profile access, company management")
        
        if transport == "streamable-http":
            print(
                f"📡 HTTP server available at http://{config.server.host}:{config.server.port}{config.server.path}"
            )
            mcp.run(
                transport=transport,
                host=config.server.host,
                port=config.server.port,
                path=config.server.path,
            )
        else:
            mcp.run(transport=transport)

    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        exit_gracefully(0)
    except Exception as e:
        logger.error(f"Server runtime error: {e}")
        print(f"\n❌ Server error: {e}")
        exit_gracefully(1)


def exit_gracefully(exit_code: int = 0) -> None:
    """Exit the application gracefully."""
    print("👋 Shutting down LinkedIn MCP server...")
    logger.info("Server shutdown complete")
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_gracefully(0)
    except Exception as e:
        logger.error(
            f"Error running MCP server: {e}",
            extra={"exception_type": type(e).__name__, "exception_message": str(e)},
        )
        print(f"❌ Error running MCP server: {e}")
        exit_gracefully(1)