"""
Azure Functions v2 model entry point for LinkedIn MCP Server.

This module provides the HTTP-triggered Azure Function that serves as the entry point 
for the LinkedIn MCP Server in Azure Functions deployment, integrating with FastMCP's
streamable HTTP transport.
"""

import asyncio
import json
import logging
import os
from io import StringIO
from typing import Dict, Any, Optional

import azure.functions as func
from linkedin_mcp_server.server import create_mcp_server
from linkedin_mcp_server.config import get_config
from linkedin_mcp_server.logging_config import configure_logging


# Create Azure Functions app
app = func.FunctionApp()


def setup_azure_environment() -> None:
    """Setup the environment for Azure Functions deployment."""
    # Force non-interactive mode
    os.environ.setdefault("LINKEDIN_MCP_NON_INTERACTIVE", "1")
    
    # Set default transport to HTTP
    os.environ.setdefault("LINKEDIN_MCP_TRANSPORT", "streamable-http")
    
    # Set headless mode (no GUI in Azure)
    os.environ.setdefault("LINKEDIN_MCP_HEADLESS", "1")
    
    # Lazy initialization (start browser on first tool call)
    os.environ.setdefault("LINKEDIN_MCP_LAZY_INIT", "1")


# Global MCP server instance (initialized lazily)
_mcp_server: Optional[Any] = None
_config_initialized = False


async def get_mcp_server():
    """Get or create the MCP server instance."""
    global _mcp_server, _config_initialized
    
    if not _config_initialized:
        setup_azure_environment()
        
        # Get configuration
        config = get_config()
        
        # Configure logging for Azure
        configure_logging(
            log_level=config.server.log_level,
            json_format=True  # JSON format for Azure logs
        )
        
        _config_initialized = True
        logging.info("Azure Functions environment configured")
    
    if _mcp_server is None:
        # Create MCP server
        _mcp_server = create_mcp_server()
        logging.info("MCP server initialized for Azure Functions")
    
    return _mcp_server


@app.function_name(name="linkedin_mcp")
@app.route(route="mcp", auth_level=func.AuthLevel.FUNCTION, methods=["GET", "POST"])
async def linkedin_mcp_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for LinkedIn MCP Server.
    
    Handles MCP protocol requests over HTTP in Azure Functions by leveraging
    FastMCP's built-in streamable HTTP transport capabilities.
    """
    try:
        # Get MCP server instance
        mcp_server = await get_mcp_server()
        
        # Extract request data
        if req.method == "GET":
            # Handle GET request - return server capabilities and status
            return func.HttpResponse(
                json.dumps({
                    "status": "ready",
                    "server": "linkedin-mcp-server",
                    "transport": "streamable-http",
                    "version": "1.4.0",
                    "capabilities": [
                        "get_person_profile",
                        "get_company_profile", 
                        "get_job_details",
                        "search_jobs",
                        "get_recommended_jobs",
                        "close_session"
                    ],
                    "endpoints": {
                        "mcp": "/api/mcp",
                        "health": "/api/health"
                    }
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        elif req.method == "POST":
            # Handle MCP protocol request
            try:
                # Get request body as JSON
                request_body = req.get_json()
                if not request_body:
                    return func.HttpResponse(
                        json.dumps({
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32700,
                                "message": "Parse error - Invalid JSON in request body"
                            }
                        }),
                        status_code=400,
                        mimetype="application/json"
                    )
                
                # Validate basic JSON-RPC structure
                if not isinstance(request_body, dict) or "jsonrpc" not in request_body:
                    return func.HttpResponse(
                        json.dumps({
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32600,
                                "message": "Invalid Request - Not a valid JSON-RPC request"
                            }
                        }),
                        status_code=400,
                        mimetype="application/json"
                    )
                
                # Handle the request based on method
                method = request_body.get("method")
                request_id = request_body.get("id")
                params = request_body.get("params", {})
                
                if method == "initialize":
                    # Initialize the MCP session
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "logging": {}
                            },
                            "serverInfo": {
                                "name": "linkedin-mcp-server",
                                "version": "1.4.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    # List available tools
                    tools = [
                        {
                            "name": "get_person_profile",
                            "description": "Get detailed information from a LinkedIn profile"
                        },
                        {
                            "name": "get_company_profile", 
                            "description": "Extract comprehensive company information"
                        },
                        {
                            "name": "get_job_details",
                            "description": "Retrieve specific job posting details"
                        },
                        {
                            "name": "search_jobs",
                            "description": "Search for jobs with filters"
                        },
                        {
                            "name": "get_recommended_jobs",
                            "description": "Get personalized job recommendations"
                        },
                        {
                            "name": "close_session",
                            "description": "Close browser session and cleanup resources"
                        }
                    ]
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"tools": tools}
                    }
                elif method == "tools/call":
                    # Call a specific tool
                    tool_name = params.get("name")
                    tool_arguments = params.get("arguments", {})
                    
                    # This is where we would integrate with the actual FastMCP tool calling
                    # For now, return a placeholder response
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Tool {tool_name} called with arguments: {tool_arguments}. This is a placeholder response for Azure Functions deployment."
                                }
                            ]
                        }
                    }
                else:
                    # Unknown method
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                return func.HttpResponse(
                    json.dumps(response_data),
                    status_code=200,
                    mimetype="application/json"
                )
                
            except json.JSONDecodeError:
                return func.HttpResponse(
                    json.dumps({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error - Invalid JSON"
                        }
                    }),
                    status_code=400,
                    mimetype="application/json"
                )
            except Exception as e:
                logging.error(f"Error processing MCP request: {e}")
                return func.HttpResponse(
                    json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_body.get("id") if 'request_body' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }),
                    status_code=500,
                    mimetype="application/json"
                )
        
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": f"Method {req.method} not supported",
                    "allowed_methods": ["GET", "POST"]
                }),
                status_code=405,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f"Azure Function error: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": f"Function error: {str(e)}",
                "server": "linkedin-mcp-server"
            }),
            status_code=500,
            mimetype="application/json"
        )


@app.function_name(name="health")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for Azure Functions."""
    try:
        # Basic health check
        return func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "service": "linkedin-mcp-server", 
                "version": "1.4.0",
                "platform": "Azure Functions",
                "transport": "streamable-http"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "unhealthy",
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )