# linkedin_mcp_server/error_handler.py
"""
Centralized error handling for LinkedIn MCP Server with structured responses.

Provides DRY approach to error handling across all tools with consistent MCP
response format, LinkedIn-specific error categorization, and proper logging.
"""

import logging
from typing import Any, Dict, List

from linkedin_mcp_server.exceptions import (
    APIError,
    AuthenticationError,
    CredentialsNotFoundError,
    LinkedInMCPError,
)

logger = logging.getLogger(__name__)


def handle_tool_error(exception: Exception, context: str = "") -> Dict[str, Any]:
    """
    Handle errors from tool functions and return structured responses.

    Args:
        exception: The exception that occurred
        context: Context about which tool failed

    Returns:
        Structured error response dictionary
    """
    return convert_exception_to_response(exception, context)


def handle_tool_error_list(
    exception: Exception, context: str = ""
) -> List[Dict[str, Any]]:
    """
    Handle errors from tool functions that return lists.

    Args:
        exception: The exception that occurred
        context: Context about which tool failed

    Returns:
        List containing structured error response dictionary
    """
    return [convert_exception_to_response(exception, context)]


def convert_exception_to_response(
    exception: Exception, context: str = ""
) -> Dict[str, Any]:
    """
    Convert an exception to a structured MCP response.

    Args:
        exception: The exception to convert
        context: Additional context about where the error occurred

    Returns:
        Structured error response dictionary
    """
    if isinstance(exception, CredentialsNotFoundError):
        return {
            "error": "authentication_not_found",
            "message": str(exception),
            "resolution": (
                "Set LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, and "
                "LINKEDIN_ACCESS_TOKEN environment variables."
            ),
        }

    if isinstance(exception, AuthenticationError):
        return {
            "error": "authentication_error",
            "message": str(exception),
            "resolution": "Verify OAuth credentials and complete the authorization flow.",
        }

    if isinstance(exception, APIError):
        return {
            "error": "api_error",
            "message": str(exception),
            "resolution": "Check API permissions and rate limits.",
        }

    if isinstance(exception, LinkedInMCPError):
        return {"error": "linkedin_error", "message": str(exception)}

    # Generic error with structured logging
    logger.error(
        "Error in %s: %s",
        context,
        exception,
        extra={
            "context": context,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        },
    )
    return {
        "error": "unknown_error",
        "message": f"Failed to execute {context}: {str(exception)}",
    }


# Keep list variant as alias for backward compatibility
convert_exception_to_list_response = handle_tool_error_list
