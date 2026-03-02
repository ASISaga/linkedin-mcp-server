# function_app.py
"""
Azure Functions entry point for the LinkedIn MCP Server.

Deployment target: Azure Functions **Flexible Consumption** plan
  - Scale-to-zero when idle; instances wake on trigger activity.
  - HTTP trigger  : synchronous MCP requests (standard JSON-RPC over HTTP).
  - Service Bus trigger: asynchronous MCP tool execution from a queue.

Architecture layers
-------------------
- This file         : Azure Functions hosting (trigger bindings, cold-start init)
- mcp_platform/     : platform-agnostic MCP factory (reusable for Reddit, etc.)
- linkedin_mcp_server/ : LinkedIn-specific tools and OAuth authentication

Environment variables expected
-------------------------------
  LINKEDIN_CLIENT_ID          LinkedIn OAuth app client ID
  LINKEDIN_CLIENT_SECRET       LinkedIn OAuth app client secret
  LINKEDIN_ACCESS_TOKEN        (optional) pre-issued access token
  SERVICE_BUS_CONNECTION_STRING  Azure Service Bus namespace connection string
  SERVICE_BUS_QUEUE_NAME         Queue name for async MCP requests (default: mcp-requests)
  APPLICATIONINSIGHTS_CONNECTION_STRING  App Insights telemetry
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import azure.functions as func

# Force non-interactive mode before any package imports that read config
os.environ.setdefault("LINKEDIN_MCP_NON_INTERACTIVE", "1")

from linkedin_mcp_server.config import get_config  # noqa: E402  (after env setup)
from linkedin_mcp_server.logging_config import configure_logging  # noqa: E402
from linkedin_mcp_server.server import create_linkedin_mcp_server  # noqa: E402

# ---------------------------------------------------------------------------
# Azure Functions app registration
# ---------------------------------------------------------------------------

app = func.FunctionApp()

# ---------------------------------------------------------------------------
# Lazy singleton – the MCP server is initialized once on the first request to
# minimise cold-start time on Flex Consumption.
# ---------------------------------------------------------------------------

_mcp_server = None


def _get_server():
    """Return the MCP server, initialising it on first call (lazy singleton)."""
    global _mcp_server
    if _mcp_server is None:
        config = get_config()
        configure_logging(config.server.log_level, json_format=True)
        _mcp_server = create_linkedin_mcp_server()
        logging.info("MCP server initialised for Azure Functions Flex Consumption")
    return _mcp_server


# ---------------------------------------------------------------------------
# MCP JSON-RPC dispatch helper
# ---------------------------------------------------------------------------


async def _dispatch(body: str) -> Dict[str, Any]:
    """
    Parse a JSON-RPC 2.0 body and dispatch to the MCP server.

    Supported MCP methods: ``initialize``, ``ping``, ``tools/list``,
    ``tools/call``.

    Returns a JSON-RPC 2.0 response dict (never raises).
    """
    # --- parse ---
    try:
        data: Dict[str, Any] = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError as exc:
        return _err(None, -32700, f"Parse error: {exc}")

    if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
        return _err(None, -32600, "Invalid Request – must be JSON-RPC 2.0")

    method: str = data.get("method", "")
    req_id: Optional[Any] = data.get("id")
    params: Dict[str, Any] = data.get("params") or {}

    # --- route ---
    try:
        server = _get_server()

        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "linkedin-mcp-server", "version": "0.1.0"},
            }

        elif method == "ping":
            result = {}

        elif method == "tools/list":
            tools = server.list_tools()
            result = {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "inputSchema": (
                            t.parameters
                            if hasattr(t, "parameters")
                            else {"type": "object", "properties": {}}
                        ),
                    }
                    for t in tools
                ]
            }

        elif method == "tools/call":
            tool_name: str = params.get("name", "")
            arguments: Dict[str, Any] = params.get("arguments") or {}
            # NOTE: FastMCP 2.x does not expose a stable public method for
            # in-process tool invocation without running the full HTTP server.
            # We use `_tool_manager.call_tool` (internal API) here because it
            # avoids spinning up a second HTTP layer inside Azure Functions.
            # If FastMCP adds a public `mcp.call_tool(name, args)` method in
            # a future release, replace this call accordingly.
            call_result = await server._tool_manager.call_tool(tool_name, arguments)
            # Normalise to MCP content list
            if isinstance(call_result, list):
                content = [
                    c.model_dump()
                    if hasattr(c, "model_dump")
                    else {"type": "text", "text": str(c)}
                    for c in call_result
                ]
            else:
                content = [
                    {
                        "type": "text",
                        "text": json.dumps(call_result)
                        if not isinstance(call_result, str)
                        else call_result,
                    }
                ]
            result = {"content": content, "isError": False}

        else:
            return _err(req_id, -32601, f"Method not found: {method}")

    except Exception as exc:
        logging.error(
            "MCP dispatch error for method '%s': %s", method, exc, exc_info=True
        )
        return _err(req_id, -32603, f"Internal error: {exc}")

    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> Dict[str, Any]:
    """Build a JSON-RPC error response."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# HTTP trigger  –  synchronous MCP-over-HTTP
# Wakes the function from scale-to-zero on each incoming request.
# ---------------------------------------------------------------------------


@app.function_name("mcp_http")
@app.route(
    route="mcp",
    auth_level=func.AuthLevel.FUNCTION,
    methods=["GET", "POST"],
)
async def mcp_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger: MCP protocol over HTTP.

    GET  → server capabilities / readiness probe.
    POST → JSON-RPC 2.0 MCP request.
    """
    if req.method == "GET":
        server = _get_server()
        tools = server.list_tools()
        return func.HttpResponse(
            json.dumps(
                {
                    "status": "ready",
                    "server": "linkedin-mcp-server",
                    "platform": "Azure Functions Flex Consumption",
                    "transport": "http",
                    "tool_count": len(tools),
                    "endpoints": {"mcp": "/api/mcp", "health": "/api/health"},
                }
            ),
            status_code=200,
            mimetype="application/json",
        )

    # POST
    try:
        raw = req.get_body()
        body = raw.decode("utf-8") if raw else "{}"
    except Exception as exc:
        return func.HttpResponse(
            json.dumps(_err(None, -32700, f"Failed to read request body: {exc}")),
            status_code=400,
            mimetype="application/json",
        )

    response_data = await _dispatch(body)
    status = 400 if "error" in response_data else 200
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=status,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# Service Bus trigger  –  asynchronous MCP tool execution
# Processes MCP JSON-RPC requests from the queue asynchronously.
# The function wakes from scale-to-zero when messages arrive in the queue.
# ---------------------------------------------------------------------------


@app.function_name("mcp_service_bus")
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="%SERVICE_BUS_QUEUE_NAME%",
    connection="SERVICE_BUS_CONNECTION_STRING",
)
async def mcp_service_bus(msg: func.ServiceBusMessage) -> None:
    """
    Service Bus trigger: asynchronous MCP tool execution.

    Receives MCP JSON-RPC requests from the ``SERVICE_BUS_QUEUE_NAME`` queue
    and executes the requested tool.  Results are emitted as structured log
    entries (Application Insights).  For request-reply scenarios, callers
    should include a ``replyTo`` queue name in the message's
    ``application_properties`` and poll that queue for results.
    """
    try:
        body = msg.get_body().decode("utf-8")
        logging.info(
            "Service Bus: processing MCP request (body_length=%d, enqueue_count=%d)",
            len(body),
            msg.enqueue_count,
        )

        response_data = await _dispatch(body)

        if "error" in response_data:
            logging.error("Service Bus: MCP error – %s", response_data["error"])
        else:
            logging.info(
                "Service Bus: MCP request completed (id=%s)", response_data.get("id")
            )

        # Emit structured result for downstream consumers / App Insights
        logging.info("MCP_RESULT: %s", json.dumps(response_data))

    except Exception as exc:
        logging.error("Service Bus trigger unhandled error: %s", exc, exc_info=True)
        # Re-raise so Azure Functions dead-letters the message after max retries
        raise


# ---------------------------------------------------------------------------
# Health check  –  anonymous, lightweight
# ---------------------------------------------------------------------------


@app.function_name("health")
@app.route(
    route="health",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=["GET"],
)
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint (anonymous, no auth key required)."""
    try:
        server = _get_server()
        tools = server.list_tools()
        return func.HttpResponse(
            json.dumps(
                {
                    "status": "healthy",
                    "server": "linkedin-mcp-server",
                    "platform": "Azure Functions Flex Consumption",
                    "tool_count": len(tools),
                }
            ),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as exc:
        logging.error("Health check failed: %s", exc)
        return func.HttpResponse(
            json.dumps({"status": "unhealthy", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )
