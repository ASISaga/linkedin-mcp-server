# Archived: Web Scraping Implementation

This directory contains the original LinkedIn web scraping implementation that was replaced
by the official LinkedIn API integration.

## Archived Files

| File | Description |
|------|-------------|
| `cli_main_old.py` | Original CLI entry point using Chrome/Selenium-based scraping |
| `setup.py` | Interactive setup flows for cookie-based authentication |
| `drivers/chrome.py` | Chrome WebDriver management for LinkedIn scraping |

## Why These Files Were Archived

The LinkedIn MCP Server migrated from web scraping to the **official LinkedIn API** to:
- Comply with LinkedIn's Terms of Service
- Use stable OAuth 2.0 authentication instead of fragile cookie-based authentication
- Leverage official API endpoints with proper rate limiting and reliability
- Enable enterprise-grade deployment without browser dependencies

## Current Implementation

The active implementation uses:
- `linkedin_mcp_server/linkedin_auth.py` – OAuth 2.0 authentication manager
- `linkedin_mcp_server/tools/` – Official API tool implementations
- `linkedin_mcp_server/server.py` – FastMCP server setup
- `linkedin_mcp_server/cli_main.py` – Updated CLI entry point

For setup instructions, see `LINKEDIN_PERMISSIONS_SETUP.md` in the project root.
