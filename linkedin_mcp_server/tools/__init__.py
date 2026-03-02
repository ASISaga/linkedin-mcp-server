# linkedin_mcp_server/tools/__init__.py
"""
LinkedIn official API tools package.

Each module in this package exports a single *registrar* function following
the ``register_<domain>_tools(mcp: FastMCP) -> None`` convention.  These
registrars are passed to ``mcp_platform.server.create_mcp_server`` to build
the LinkedIn MCP server, and can be composed in any combination.

Modules
-------
auth.py     OAuth lifecycle, token management, server info
person.py   Profile access, email, post creation
company.py  Organisation info, posts, follower/page statistics
job.py      Job postings, applications, analytics
social.py   Reactions, comments, UGC posts, shares, social metadata

This same registrar pattern makes it straightforward to build an equivalent
server for any other platform (e.g. Reddit) without touching the MCP or
Azure hosting layers.
"""
