"""
Azure Functions v2 model entry point for LinkedIn MCP Server.

This module provides the HTTP-triggered Azure Function that serves as the entry point 
for the LinkedIn MCP Server in Azure Functions deployment, using a custom adapter
to integrate with FastMCP's capabilities.
"""

import json
import logging
import asyncio
from typing import Dict, Any

import azure.functions as func
from azure_functions_adapter import adapter


# Create Azure Functions app
app = func.FunctionApp()


@app.function_name(name="linkedin_mcp")
@app.route(route="mcp", auth_level=func.AuthLevel.FUNCTION, methods=["GET", "POST"])
async def linkedin_mcp_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for LinkedIn MCP Server.
    
    Handles MCP protocol requests over HTTP in Azure Functions by using
    the custom Azure Functions adapter that integrates with FastMCP.
    """
    try:
        # Determine request method and body
        method = req.method
        
        if method == "GET":
            # Handle GET request through adapter
            response = await adapter.handle_mcp_request("", method="GET")
        
        elif method == "POST":
            # Get request body
            try:
                request_body = req.get_body()
                if request_body:
                    # Decode bytes to string
                    body_str = request_body.decode('utf-8')
                else:
                    body_str = "{}"
                
                # Handle POST request through adapter
                response = await adapter.handle_mcp_request(body_str, method="POST")
                
            except Exception as e:
                logging.error(f"Error parsing request body: {e}")
                return func.HttpResponse(
                    json.dumps({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }),
                    status_code=400,
                    mimetype="application/json"
                )
        
        else:
            response = await adapter.handle_mcp_request("", method=method)
        
        # Return the response from the adapter
        return func.HttpResponse(
            response["body"],
            status_code=response["status_code"],
            mimetype=response["headers"].get("Content-Type", "application/json")
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
                "transport": "streamable-http",
                "endpoints": {
                    "mcp": "/api/mcp",
                    "health": "/api/health"
                }
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