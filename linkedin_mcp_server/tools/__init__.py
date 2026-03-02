# src/linkedin_mcp_server/tools/__init__.py
"""
LinkedIn official API tools package.

This package contains the MCP tool implementations for LinkedIn data access
using the official LinkedIn REST API with OAuth 2.0 authentication.

Available Tool Modules:
- person.py: Profile access, email, OAuth flow, and user post creation
- company.py: Organization info, company posts, follower/page statistics
- job.py: Job postings management, applications, and analytics
- social.py: Reactions, comments, UGC posts, shares, and social metadata

Architecture:
- FastMCP integration for MCP-compliant tool registration
- OAuth 2.0 authentication via linkedin-api-client
- Consistent structured data return format for all tools
"""
