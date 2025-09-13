# LinkedIn MCP Server (Official API)

<p align="left">
  <a href="https://github.com/stickerdaniel/linkedin-mcp-server/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/stickerdaniel/linkedin-mcp-server/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI Status"></a>
  <a href="https://github.com/stickerdaniel/linkedin-mcp-server/actions/workflows/release.yml" target="_blank"><img src="https://github.com/stickerdaniel/linkedin-mcp-server/actions/workflows/release.yml/badge.svg?branch=main" alt="Release"></a>
  <a href="https://github.com/stickerdaniel/linkedin-mcp-server/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/badge/License-Apache%202.0-brightgreen?labelColor=32383f" alt="License"></a>
</p>

**⚡ NOW USING OFFICIAL LINKEDIN API ⚡**

Through this LinkedIn MCP server, AI assistants like Claude can connect to LinkedIn using the **official LinkedIn API** with proper OAuth 2.0 authentication. This ensures compliance with LinkedIn's Terms of Service and provides enterprise-grade reliability.

## 🔄 Migration Completed: Web Scraping → Official API

This server has been **fully migrated** from web scraping to the official LinkedIn API:

✅ **What Changed:**
- Web scraping → Official LinkedIn REST API
- Cookie authentication → OAuth 2.0 with access tokens  
- Chrome/Selenium → HTTP API client
- Terms violation → Fully compliant API usage

⚠️ **Important Limitations:**
- **Profile access**: Only your own authenticated profile (not public profiles)
- **Company access**: Only companies you manage or have admin access to
- **Job access**: Only job postings from your companies  
- **No public search**: Cannot search arbitrary profiles/companies/jobs

🎯 **New Capabilities:**
- OAuth 2.0 authentication flow
- Compliant LinkedIn API usage
- Enterprise-ready architecture  
- Stable API contract (no breaking changes from UI updates)

## 🚀 Quick Start with Official API

### 1. Prerequisites
- LinkedIn Developer Account
- LinkedIn Developer Application with OAuth credentials

### 2. Setup LinkedIn Developer App
```bash
# See detailed setup guide
cat LINKEDIN_PERMISSIONS_SETUP.md
```

### 3. Configure OAuth Credentials
```bash
export LINKEDIN_CLIENT_ID="your_client_id"
export LINKEDIN_CLIENT_SECRET="your_client_secret"
export LINKEDIN_REDIRECT_URI="http://localhost:8000/auth/callback"

# Optional: Direct access token for testing
export LINKEDIN_ACCESS_TOKEN="your_access_token"
```

### 4. Install and Run
```bash
# Install dependencies
pip install linkedin-api-client fastmcp keyring python-dotenv

# Run the server
python -m linkedin_mcp_server
```

### 5. OAuth Authentication Flow
1. Use `get_oauth_authorization_url` tool to get authorization URL
2. Direct user to authorization URL for consent  
3. Get authorization code from callback
4. Use `exchange_oauth_code` to get access token
5. Use API with authenticated access token

## Installation Methods

[![Azure Functions](https://img.shields.io/badge/Azure_Functions-Cloud_Deployment-0078d4?style=for-the-badge&logo=microsoft-azure&logoColor=0078d4)](#-azure-functions-deployment-recommended---cloud)
[![Install DXT Extension](https://img.shields.io/badge/Claude_Desktop_DXT-d97757?style=for-the-badge&logo=anthropic)](#-claude-desktop-dxt-extension)
[![uvx](https://img.shields.io/badge/uvx-Quick_Install-de5fe9?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDEiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCA0MSA0MSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTS01LjI4NjE5ZS0wNiAwLjE2ODYyOUwwLjA4NDMwOTggMjAuMTY4NUwwLjE1MTc2MiAzNi4xNjgzQzAuMTYxMDc1IDM4LjM3NzQgMS45NTk0NyA0MC4xNjA3IDQuMTY4NTkgNDAuMTUxNEwyMC4xNjg0IDQwLjA4NEwzMC4xNjg0IDQwLjA0MThMMzEuMTg1MiA0MC4wMzc1QzMzLjM4NzcgNDAuMDI4MiAzNS4xNjgzIDM4LjIwMjYgMzUuMTY4MyAzNlYzNkwzNy4wMDAzIDM2TDM3LjAwMDMgMzkuOTk5Mkw0MC4xNjgzIDM5Ljk5OTZMMzkuOTk5NiAtOS45NDY1M2UtMDdMMjEuNTk5OCAwLjA3NzU2ODlMMjEuNjc3NCAxNi4wMTg1TDIxLjY77NCwyNS45OTk4TDIwLjA3NzQgMjUuOTk5OEwxOC4zOTk4IDI1Ljk5OThMMTguNDc3NCAxNi4wMzJMMTguMzk5OCAwLjA5MTA1OTNMLTUUMITIG5ZS0wNiAwLjE2ODYyOVoiIGZpbGw9IiNERTVGRTkiLz4KPC9zdmc+Cg==)](#-uvx-setup-quick-install---universal)
[![Development](https://img.shields.io/badge/Development-Local-ffdc53?style=for-the-badge&logo=python&logoColor=ffdc53)](#-local-setup-develop--contribute)

https://github.com/user-attachments/assets/eb84419a-6eaf-47bd-ac52-37bc59c83680

## Usage Examples (Official API)
```
Help me set up OAuth authentication with LinkedIn
```
```
Get my LinkedIn profile information
```
```
What companies do I have admin access to on LinkedIn?
```
```
Show me job postings from companies I manage
```
```
What are the limitations of the official LinkedIn API?
```

## Features & Tool Status (Official LinkedIn API)
> [!TIP]
> - **OAuth Authentication** (`get_oauth_authorization_url`, `exchange_oauth_code`): Complete OAuth 2.0 flow for secure API access
> - **Profile Access** (`get_current_user_profile`): Get authenticated user's LinkedIn profile information
> - **Token Management** (`get_token_info`, `refresh_access_token`): Manage and refresh access tokens
> - **Company Management** (`search_companies`, `get_managed_companies`): Access companies you manage
> - **Job Management** (`search_job_postings`, `create_job_posting`): Manage job postings for your companies
> - **API Information** (`get_api_migration_info`): Learn about API capabilities and limitations

> [!IMPORTANT]
> **API Limitations**: The official LinkedIn API has significant restrictions compared to web scraping:
> - **Profile access**: Only your own authenticated profile
> - **Company access**: Only companies you manage or have admin permissions for
> - **Job access**: Only job postings from companies you manage
> - **No public search**: Cannot access arbitrary public profiles, companies, or job listings
> 
> These limitations are imposed by LinkedIn's official API and ensure compliance with their Terms of Service.

<br/>
<br/>

## ☁️ Azure Functions Deployment (Recommended - Cloud)

**Prerequisites:** [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) and [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) installed.

### Quick Deployment

Run the automated deployment script:

```bash
# Make the script executable
chmod +x azure-deploy.sh

# Run deployment (will prompt for configuration)
./azure-deploy.sh
```

The script will:
1. Create Azure resource group
2. Set up Function App with consumption plan  
3. Deploy the LinkedIn MCP Server
4. Configure environment variables
5. Provide access URLs

### Manual Deployment

**1. Login to Azure:**
```bash
az login
```

**2. Create resources:**
```bash
# Create resource group
az group create --name linkedin-mcp-rg --location "East US"

# Create storage account  
az storage account create --name linkedinmcpstorage --location "East US" --resource-group linkedin-mcp-rg --sku Standard_LRS

# Create function app
az functionapp create --resource-group linkedin-mcp-rg --consumption-plan-location "East US" --runtime python --runtime-version 3.11 --functions-version 4 --name linkedin-mcp-server --storage-account linkedinmcpstorage
```

**3. Deploy and configure:**
```bash
# Deploy the function
func azure functionapp publish linkedin-mcp-server

# Set LinkedIn cookie
az functionapp config appsettings set --name linkedin-mcp-server --resource-group linkedin-mcp-rg --settings LINKEDIN_COOKIE="your_linkedin_cookie_here"
```

### Getting the LinkedIn Cookie

<details>
<summary><b>🌐 Chrome DevTools Guide</b></summary>

1. Open LinkedIn and login
2. Open Chrome DevTools (F12 or right-click → Inspect)
3. Go to **Application** > **Storage** > **Cookies** > **https://www.linkedin.com**
4. Find the cookie named `li_at`
5. Copy the **Value** field (this is your LinkedIn session cookie)
6. Use this value as your `LINKEDIN_COOKIE` in the Azure Function settings

</details>

### Usage

Once deployed, your LinkedIn MCP Server will be available at:
- **Health Check**: `https://your-function-app.azurewebsites.net/api/health`
- **MCP Endpoint**: `https://your-function-app.azurewebsites.net/api/mcp`

**Client Configuration for Azure Functions:**
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "curl",
      "args": [
        "-X", "POST", 
        "https://your-function-app.azurewebsites.net/api/mcp",
        "-H", "Content-Type: application/json",
        "-d", "@-"
      ]
    }
  }
}
```

### Azure Functions Benefits

- **Serverless**: No server management required
- **Auto-scaling**: Automatically scales based on demand
- **Pay-per-use**: Only pay for actual executions
- **High availability**: Built-in redundancy and failover
- **Integrated monitoring**: Azure Application Insights included
- **Secure**: Function-level authentication and Azure security

### Cost Estimation

Azure Functions consumption plan pricing:
- **Free tier**: 1 million requests and 400,000 GB-seconds per month
- **Beyond free tier**: $0.20 per million executions + $0.000016/GB-second
- **Typical cost**: $5-20/month for moderate usage (100-500 LinkedIn operations/day)

> [!NOTE]
> The cookie will expire after 30 days. Update the `LINKEDIN_COOKIE` environment variable in Azure when needed.

<details>
<summary><b>🔧 Advanced Configuration</b></summary>

**Environment Variables:**
- `LINKEDIN_COOKIE` - LinkedIn session cookie (required)
- `LINKEDIN_MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `LINKEDIN_MCP_HEADLESS` - Run browser in headless mode (default: 1)
- `LINKEDIN_MCP_LAZY_INIT` - Initialize browser on first request (default: 1)

**Monitoring:**
```bash
# View live logs
az functionapp logs tail --name linkedin-mcp-server --resource-group linkedin-mcp-rg

# Enable Application Insights for detailed monitoring
az monitor app-insights component create --app linkedin-mcp-server --location "East US" --resource-group linkedin-mcp-rg
```

</details>

<details>
<summary><b>❗ Troubleshooting</b></summary>

**Common Issues:**
- **Function timeout**: Default timeout is 5 minutes. Browser initialization takes 10-30 seconds on cold start.
- **Memory limits**: Chrome requires significant memory. Consider Premium plan for heavy usage.
- **LinkedIn blocking**: Use valid cookies and avoid excessive requests.

**Debug locally:**
```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Run locally
func start

# Test locally
curl http://localhost:7071/api/health
```

</details>

<br/>
<br/>

## 📦 Claude Desktop (DXT Extension)

**Prerequisites:** [Claude Desktop](https://claude.ai/download) installed

**One-click installation** for Claude Desktop users:
1. Download the [DXT extension](https://github.com/stickerdaniel/linkedin-mcp-server/releases/latest)
2. Double-click to install into Claude Desktop
3. Set your LinkedIn cookie in the extension settings

> [!NOTE]
> The DXT extension now uses the uvx installation method internally instead of Docker for better compatibility and performance.

### Getting the LinkedIn Cookie
<details>
<summary><b>🌐 Chrome DevTools Guide</b></summary>

1. Open LinkedIn and login
2. Open Chrome DevTools (F12 or right-click → Inspect)
3. Go to **Application** > **Storage** > **Cookies** > **https://www.linkedin.com**
4. Find the cookie named `li_at`
5. Copy the **Value** field (this is your LinkedIn session cookie)
6. Use this value as your `LINKEDIN_COOKIE` in the configuration

</details>

> [!NOTE]
> The cookie will expire during the next 30 days. Just get the new cookie and update your client config. There are also many cookie manager extensions that you can use to quickly copy the cookie.

### DXT Extension Setup Help
<details>
<summary><b>❗ Troubleshooting</b></summary>

**Installation issues:**
- Ensure you have Claude Desktop installed
- Download the latest DXT extension from releases

**Login issues:**
- Ensure your LinkedIn cookie is set and correct
- Make sure you have only one active LinkedIn session per cookie at a time. Trying to open multiple sessions with the same cookie will result in a cookie invalid error.
- LinkedIn may require a login confirmation in the LinkedIn mobile app
- You might get a captcha challenge if you logged in a lot of times in a short period of time, then try again later or follow the [local setup instructions](#-local-setup-develop--contribute) to run the server manually in --no-headless mode where you can debug the login process (solve captcha manually)
</details>

<br/>
<br/>

## 🚀 uvx Setup (Quick Install - Universal)

**Prerequisites:** Make sure you have [uv](https://docs.astral.sh/uv/) installed.

### Installation

Run directly from GitHub without cloning:

```bash
# Run directly from GitHub (latest version)
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --help

# Run with your LinkedIn cookie
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --cookie "li_at=YOUR_COOKIE_VALUE"
```

### Getting the LinkedIn Cookie
<details>
<summary><b>🌐 Chrome DevTools Guide</b></summary>

1. Open LinkedIn and login
2. Open Chrome DevTools (F12 or right-click → Inspect)
3. Go to **Application** > **Storage** > **Cookies** > **https://www.linkedin.com**
4. Find the cookie named `li_at`
5. Copy the **Value** field (this is your LinkedIn session cookie)
6. Use this value as your `LINKEDIN_COOKIE` in the configuration

</details>

<details>
<summary><b>🚀 uvx get-cookie method</b></summary>

**Run the server with the `--get-cookie` flag:**
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server \
  linkedin-mcp-server --get-cookie
```
Copy the cookie from the output and set it as `LINKEDIN_COOKIE` in your client configuration. If this fails with a captcha challenge, use the Chrome DevTools method above.
</details>

> [!NOTE]
> The cookie will expire during the next 30 days. Just get the new cookie and update your client config. There are also many cookie manager extensions that you can use to quickly copy the cookie.

### uvx Setup Help
<details>
<summary><b>🔧 Configuration</b></summary>

**Client Configuration:**
```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/stickerdaniel/linkedin-mcp-server",
        "linkedin-mcp-server"
      ],
      "env": {
        "LINKEDIN_COOKIE": "li_at=YOUR_COOKIE_VALUE"
      }
    }
  }
}
```

**Transport Modes:**
- **Default (stdio)**: Standard communication for local MCP servers
- **Streamable HTTP**: For web-based MCP server

**CLI Options:**
- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Set logging level (default: WARNING)
- `--no-lazy-init` - Login to LinkedIn immediately instead of waiting for the first tool call
- `--transport {stdio,streamable-http}` - Set transport mode
- `--host HOST` - HTTP server host (default: 127.0.0.1)
- `--port PORT` - HTTP server port (default: 8000)
- `--path PATH` - HTTP server path (default: /mcp)
- `--get-cookie` - Attempt to login with email and password and extract the LinkedIn cookie
- `--cookie {cookie}` - Pass a specific LinkedIn cookie for login
- `--user-agent {user_agent}` - Specify custom user agent string to prevent anti-scraping detection

**Basic Usage Examples:**
```bash
# Run with cookie from environment variable
LINKEDIN_COOKIE="YOUR_COOKIE_VALUE" uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server

# Run with cookie via flag
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --cookie "YOUR_COOKIE_VALUE"

# Run with debug logging
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --log-level DEBUG

# Extract cookie with credentials
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --get-cookie
```

**HTTP Mode Example (for web-based MCP clients):**
```bash
uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server \
  --transport streamable-http --host 127.0.0.1 --port 8080 --path /mcp
```

**Test with mcp inspector:**
1. Install and run mcp inspector ```bunx @modelcontextprotocol/inspector```
2. Click pre-filled token url to open the inspector in your browser
3. Select `Streamable HTTP` as `Transport Type`
4. Set `URL` to `http://localhost:8080/mcp`
5. Connect
6. Test tools

</details>

<details>
<summary><b>❗ Troubleshooting</b></summary>

**Installation issues:**
- Ensure you have uv installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Check uv version: `uv --version` (should be 0.4.0 or higher)

**Cookie issues:**
- Ensure your LinkedIn cookie is set and correct
- Cookie can be passed via `--cookie` flag or `LINKEDIN_COOKIE` environment variable
- Make sure you have only one active LinkedIn session per cookie at a time

**Login issues:**
- LinkedIn may require a login confirmation in the LinkedIn mobile app for --get-cookie
- You might get a captcha challenge if you logged in a lot of times in a short period
</details>

<br/>
<br/>

## 🐍 Local Setup (Develop & Contribute)

**Prerequisites:** [Chrome browser](https://www.google.com/chrome/) and [Git](https://git-scm.com/downloads) installed

**ChromeDriver Setup:**
1. **Check Chrome version**: Chrome → menu (⋮) → Help → About Google Chrome
2. **Download matching ChromeDriver**: [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
3. **Make it accessible**:
   - Place ChromeDriver in PATH (`/usr/local/bin` on macOS/Linux)
   - Or set: `export CHROMEDRIVER_PATH=/path/to/chromedriver`
   - if no CHROMEDRIVER_PATH is set, the server will try to find it automatically by checking common locations

### Installation

```bash
# 1. Clone repository
git clone https://github.com/stickerdaniel/linkedin-mcp-server
cd linkedin-mcp-server

# 2. Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python # install python if you don't have it

# 3. Install dependencies and dev dependencies
uv sync
uv sync --group dev

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Start the server once manually
# You will be prompted to enter your LinkedIn credentials, and they will be securely stored in your OS keychain
# Once logged in, your cookie will be stored in your OS keychain and used for subsequent runs until it expires
uv run -m linkedin_mcp_server --no-headless --no-lazy-init
```

### Local Setup Help
<details>
<summary><b>🔧 Configuration</b></summary>

**CLI Options:**
- `--no-headless` - Show browser window (debugging)
- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Set logging level (default: WARNING)
- `--no-lazy-init` - Login to LinkedIn immediately instead of waiting for the first tool call
- `--get-cookie` - Login with email and password and extract the LinkedIn cookie
- `--clear-keychain` - Clear all stored LinkedIn credentials and cookies from system keychain
- `--cookie {cookie}` - Pass a specific LinkedIn cookie for login
- `--user-agent {user_agent}` - Specify custom user agent string to prevent anti-scraping detection
- `--transport {stdio,streamable-http}` - Set transport mode
- `--host HOST` - HTTP server host (default: 127.0.0.1)
- `--port PORT` - HTTP server port (default: 8000)
- `--path PATH` - HTTP server path (default: /mcp)
- `--help` - Show help

**HTTP Mode Example (for web-based MCP clients):**
```bash
uv run -m linkedin_mcp_server --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

**Claude Desktop:**
```**json**
{
  "mcpServers": {
    "linkedin": {
      "command": "uv",
      "args": ["--directory", "/path/to/linkedin-mcp-server", "run", "-m", "linkedin_mcp_server"]
    }
  }
}
```

</details>

<details>
<summary><b>❗ Troubleshooting</b></summary>

**Login/Scraping issues:**
- Use `--no-headless` to see browser actions (captcha challenge, LinkedIn mobile app 2fa, ...)
- Add `--no-lazy-init` to attempt to login to LinkedIn immediately instead of waiting for the first tool call
- Add `--log-level DEBUG` to see more detailed logging
- Make sure you have only one active LinkedIn session per cookie at a time. Trying to open multiple sessions with the same cookie will result in a cookie invalid error. E.g. if you have a logged in browser session with a docker container, you can't use the same cookie to login with the local setup while the docker container is running / session is not closed.

**ChromeDriver issues:**
- Ensure Chrome and ChromeDriver versions match
- Check ChromeDriver is in PATH or set `CHROMEDRIVER_PATH` in your env

**Python issues:**
- Check Python version: `uv python --version` (should be 3.12+)
- Reinstall dependencies: `uv sync --reinstall`

</details>

Feel free to open an [issue](https://github.com/stickerdaniel/linkedin-mcp-server/issues) or [PR](https://github.com/stickerdaniel/linkedin-mcp-server/pulls)!


<br/>
<br/>


## Acknowledgements
Built with [LinkedIn Scraper](https://github.com/joeyism/linkedin_scraper) by [@joeyism](https://github.com/joeyism) and [FastMCP](https://gofastmcp.com/).

⚠️ Use in accordance with [LinkedIn's Terms of Service](https://www.linkedin.com/legal/user-agreement). Web scraping may violate LinkedIn's terms. This tool is for personal use only.

## Star History

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date" />
  <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=stickerdaniel/linkedin-mcp-server&type=Date" />
</picture>


## License

This project is licensed under the Apache 2.0 license.

<br>
