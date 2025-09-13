# Azure Functions Migration - Technical Implementation Notes

This document explains the technical implementation details of the Azure Functions migration for the LinkedIn MCP Server.

## Architecture Changes

### Original Docker Implementation
- **Container-based**: Ran as a Docker container with Python + Chrome
- **CLI Application**: Used `linkedin_mcp_server.cli_main:main` as entry point
- **Transport Modes**: Supported both `stdio` and `streamable-http`
- **Interactive Setup**: Could prompt users for credentials
- **Process Management**: Long-running process with cleanup on exit

### New Azure Functions Implementation
- **Serverless**: Runs on Azure Functions consumption plan
- **HTTP Triggers**: Uses Azure Functions HTTP triggers for requests
- **HTTP Transport Only**: Only supports HTTP transport (MCP over HTTP)
- **Non-Interactive**: Credentials must be provided via environment variables
- **Stateless**: Each request is independent, no persistent state

## Key Components

### 1. `function_app.py`
The main Azure Functions entry point that defines HTTP-triggered functions:
- `linkedin_mcp` - Main MCP endpoint at `/api/mcp`
- `health` - Health check endpoint at `/api/health`

### 2. `azure_functions_adapter.py`
Custom adapter that bridges Azure Functions HTTP requests with MCP protocol:
- Handles JSON-RPC protocol parsing
- Manages server initialization and configuration
- Provides Azure-specific environment setup
- Routes MCP requests to appropriate handlers

### 3. Configuration Updates
Enhanced `linkedin_mcp_server/config/loaders.py` to support:
- Azure Functions environment variables (`LINKEDIN_MCP_*` prefixed)
- Non-interactive mode detection
- Automatic Azure Functions detection via `FUNCTIONS_WORKER_RUNTIME`

### 4. Azure Functions Configuration Files
- `host.json` - Azure Functions runtime configuration
- `local.settings.json` - Local development settings template
- `requirements.txt` - Azure Functions specific dependencies

## Environment Variables

### Azure Functions Specific
- `LINKEDIN_MCP_NON_INTERACTIVE=1` - Forces non-interactive mode
- `LINKEDIN_MCP_TRANSPORT=streamable-http` - Sets HTTP transport
- `LINKEDIN_MCP_HEADLESS=1` - Enables headless browser mode
- `LINKEDIN_MCP_LAZY_INIT=1` - Enables lazy browser initialization
- `LINKEDIN_MCP_LOG_LEVEL=WARNING` - Sets logging level

### Existing Variables (Still Supported)
- `LINKEDIN_COOKIE` - LinkedIn session cookie (required)
- `LOG_LEVEL` - Alternative logging level setting
- `HEADLESS` - Alternative headless mode setting

## MCP Protocol Implementation

### Supported Methods
1. **initialize** - Initialize MCP session
2. **tools/list** - List available LinkedIn tools
3. **tools/call** - Execute LinkedIn tools (placeholder in current implementation)

### Tool Definitions
The adapter provides static tool definitions for:
- `get_person_profile` - LinkedIn profile scraping
- `get_company_profile` - Company profile scraping  
- `get_job_details` - Job posting details
- `search_jobs` - Job search functionality
- `get_recommended_jobs` - Personalized job recommendations
- `close_session` - Browser session cleanup

## Cold Start Considerations

### Browser Initialization
- Chrome browser initialization takes 10-30 seconds on cold start
- Lazy initialization delays browser startup until first tool call
- Browser remains warm between requests within the same instance

### Memory Usage
- Chrome requires 200-500MB memory per instance
- Azure Functions consumption plan provides up to 1.5GB memory
- Premium plan recommended for heavy usage scenarios

## Security Model

### Authentication
- Function-level authentication (access keys required)
- LinkedIn cookie stored as environment variable
- No credentials stored in code or logs

### Network Isolation
- Outbound HTTPS connections only (to LinkedIn)
- No inbound connections except HTTP triggers
- Azure network security groups can restrict access

## Deployment Process

### Automated Deployment (`azure-deploy.sh`)
1. Create Azure resource group
2. Create storage account for function state
3. Create Azure Functions app with consumption plan
4. Deploy function code using Azure Functions Core Tools
5. Configure environment variables
6. Test deployment with health check

### Manual Deployment
Uses standard Azure CLI and Functions Core Tools commands as documented in README-azure.md.

## Limitations and Considerations

### Current Implementation Limitations
- Tool execution is currently placeholder (returns test responses)
- No persistent session state between requests
- Browser instances are created per tool execution

### Future Improvements Needed
1. **Full FastMCP Integration**: Complete integration with FastMCP's tool execution system
2. **Connection Pooling**: Reuse browser instances across requests
3. **State Management**: Implement session persistence for multi-request workflows
4. **Error Handling**: Enhanced error handling and retry mechanisms
5. **Monitoring**: Integration with Azure Application Insights

### Cost Optimization
- Use consumption plan for variable workloads
- Consider premium plan for consistent heavy usage
- Monitor execution time and memory usage
- Implement request batching for efficiency

## Testing Strategy

### Local Testing
- Use Azure Functions Core Tools for local development
- Test with `func start` command
- Validate MCP protocol responses manually

### Integration Testing  
- Test actual LinkedIn scraping functionality
- Verify browser automation works in Azure environment
- Performance testing under load

### Monitoring
- Azure Application Insights for performance metrics
- Function execution logs for debugging
- LinkedIn API rate limiting monitoring

## Migration Path

### For Existing Docker Users
1. Export LinkedIn cookie from existing setup
2. Deploy Azure Functions version using provided scripts
3. Update MCP client configuration to use HTTP endpoints
4. Test functionality with existing workflows
5. Decommission Docker container

### Rollback Strategy
- Original Docker implementation remains in git history
- Can restore Docker files if needed
- uvx and local development methods still available as alternatives

## Dependencies

### New Dependencies Added
- `azure-functions>=1.18.0` - Azure Functions Python bindings
- `azure-functions-worker>=1.0.0` - Azure Functions runtime worker

### Existing Dependencies Maintained
- `fastmcp>=2.10.1` - MCP protocol implementation
- `linkedin-scraper` - LinkedIn scraping functionality
- All other existing dependencies unchanged

This migration provides a scalable, serverless alternative to the Docker deployment while maintaining compatibility with the MCP protocol and LinkedIn functionality.