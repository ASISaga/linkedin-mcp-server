# src/linkedin_mcp_server/config/schema.py
"""
Configuration schema definitions for LinkedIn MCP Server.

This module defines the dataclass schemas that represent the application's configuration
structure. It provides type-safe configuration objects with validation and default values
for all aspects of the server including LinkedIn OAuth credentials and MCP server parameters.

Key Components:
- LinkedInConfig: LinkedIn OAuth authentication and connection settings
- ServerConfig: MCP server transport and operational settings
- AppConfig: Main application configuration combining all components
"""

from dataclasses import dataclass, field
from typing import Literal, Optional


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""

    pass


@dataclass
class LinkedInConfig:
    """LinkedIn OAuth 2.0 configuration for official API access."""

    # OAuth 2.0 credentials
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: str = "http://localhost:8000/auth/callback"

    # Access token (for direct API access without OAuth flow)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    # Legacy scraping credentials (kept for backward compatibility only)
    email: Optional[str] = None
    password: Optional[str] = None
    cookie: Optional[str] = None


@dataclass
class ServerConfig:
    """MCP server configuration."""

    transport: Literal["stdio", "streamable-http"] = "stdio"
    transport_explicitly_set: bool = False  # Track if transport was explicitly set
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "WARNING"

    # HTTP transport configuration
    host: str = "127.0.0.1"
    port: int = 8000
    path: str = "/mcp"

    # OAuth flow configuration
    oauth_flow: bool = False  # Enable OAuth flow for authentication


@dataclass
class AppConfig:
    """Main application configuration."""

    linkedin: LinkedInConfig = field(default_factory=LinkedInConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    is_interactive: bool = field(default=False)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate_transport_config()
        self._validate_port_range()
        self._validate_path_format()

    def _validate_transport_config(self) -> None:
        """Validate transport configuration is consistent."""
        if self.server.transport == "streamable-http":
            if not self.server.host:
                raise ConfigurationError("HTTP transport requires a valid host")
            if not self.server.port:
                raise ConfigurationError("HTTP transport requires a valid port")

    def _validate_port_range(self) -> None:
        """Validate port is in valid range."""
        if not (1 <= self.server.port <= 65535):
            raise ConfigurationError(
                f"Port {self.server.port} is not in valid range (1-65535)"
            )

    def _validate_path_format(self) -> None:
        """Validate path format for HTTP transport."""
        if self.server.transport == "streamable-http":
            if not self.server.path.startswith("/"):
                raise ConfigurationError(
                    f"HTTP path '{self.server.path}' must start with '/'"
                )
            if len(self.server.path) < 2:
                raise ConfigurationError(
                    f"HTTP path '{self.server.path}' must be at least 2 characters"
                )
