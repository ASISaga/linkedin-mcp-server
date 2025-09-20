# Azure Functions Deployment for LinkedIn MCP Server

This directory contains the Azure Functions v2 model implementation for the LinkedIn MCP Server.

## Files Structure

```
function_app.py           # Main Azure Functions entry point
host.json                 # Azure Functions host configuration
local.settings.json       # Local development settings
pyproject.toml            # Python dependencies for Azure Functions
azure-deploy.sh           # Deployment script
README-azure.md          # This file
```

## Prerequisites

1. **Azure CLI**: Install [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Functions Core Tools**: Install [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3. **LinkedIn Cookie**: You'll need a valid LinkedIn `li_at` cookie

## Local Development

1. **Install Azure Functions Core Tools**:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Configure local settings**:
   ```bash
   # Copy the template and fill in your values
   cp local.settings.json.example local.settings.json
   
   # Edit local.settings.json and add your LinkedIn cookie:
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "UseDevelopmentStorage=true",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "LINKEDIN_COOKIE": "your_linkedin_li_at_cookie_here"
     }
   }
   ```

3. **Run locally**:
   ```bash
   func start
   ```

   The function will be available at:
   - MCP endpoint: `http://localhost:7071/api/mcp`
   - Health check: `http://localhost:7071/api/health`

## Azure Deployment

### Option 1: Using Azure CLI (Recommended)

1. **Login to Azure**:
   ```bash
   az login
   ```

2. **Create Resource Group**:
   ```bash
   az group create --name linkedin-mcp-rg --location "East US"
   ```

3. **Create Storage Account**:
   ```bash
   az storage account create --name linkedinmcpstorage --location "East US" --resource-group linkedin-mcp-rg --sku Standard_LRS
   ```

4. **Create Function App**:
   ```bash
   az functionapp create --resource-group linkedin-mcp-rg --consumption-plan-location "East US" --runtime python --runtime-version 3.11 --functions-version 4 --name linkedin-mcp-server --storage-account linkedinmcpstorage
   ```

5. **Deploy the Function**:
   ```bash
   func azure functionapp publish linkedin-mcp-server
   ```

6. **Configure Environment Variables**:
   ```bash
   az functionapp config appsettings set --name linkedin-mcp-server --resource-group linkedin-mcp-rg --settings LINKEDIN_COOKIE="your_linkedin_cookie_here"
   ```

### Option 2: Using the Deployment Script

1. **Make the script executable**:
   ```bash
   chmod +x azure-deploy.sh
   ```

2. **Run the deployment script**:
   ```bash
   ./azure-deploy.sh
   ```

   The script will prompt you for:
   - Resource group name
   - Function app name
   - LinkedIn cookie
   - Azure region

## Environment Variables

The following environment variables can be set in Azure Functions:

| Variable | Description | Default |
|----------|-------------|---------|
| `LINKEDIN_COOKIE` | LinkedIn session cookie (`li_at` value) | Required |
| `LINKEDIN_MCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | WARNING |
| `LINKEDIN_MCP_HEADLESS` | Run browser in headless mode | 1 (true) |
| `LINKEDIN_MCP_LAZY_INIT` | Initialize browser on first request | 1 (true) |
| `LINKEDIN_MCP_TRANSPORT` | Transport mode (always streamable-http) | streamable-http |
| `LINKEDIN_MCP_NON_INTERACTIVE` | Force non-interactive mode | 1 (true) |

## Usage

Once deployed, you can use the LinkedIn MCP Server through HTTP requests:

### Health Check
```bash
curl https://your-function-app.azurewebsites.net/api/health
```

### MCP Protocol
The MCP endpoint accepts JSON-RPC requests:

```bash
curl -X POST https://your-function-app.azurewebsites.net/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### Available Tools

- `get_person_profile` - Get LinkedIn profile information
- `get_company_profile` - Get company profile information  
- `get_job_details` - Get job posting details
- `search_jobs` - Search for jobs
- `get_recommended_jobs` - Get personalized job recommendations
- `close_session` - Close browser session

## Monitoring

Use Azure Application Insights to monitor your function:

1. **Enable Application Insights** in the Azure portal
2. **View logs** in the Application Insights dashboard
3. **Set up alerts** for errors or performance issues

## Cost Considerations

Azure Functions consumption plan charges are based on:
- **Executions**: Number of function invocations
- **Execution Time**: Total execution time (GB-seconds)
- **Memory Usage**: Peak memory usage during execution

For LinkedIn scraping workloads:
- Each profile/company/job scraping operation takes ~5-15 seconds
- Memory usage is typically 200-500MB per execution
- Browser initialization adds ~3-5 seconds on first request

## Security

- Function uses **Function-level authorization** by default
- Add **API Key authentication** for production use
- Store LinkedIn cookies as **Azure Key Vault secrets** for enhanced security
- Consider **IP restrictions** to limit access

## Troubleshooting

### Common Issues

1. **LinkedIn authentication fails**:
   - Verify your `li_at` cookie is valid and not expired
   - LinkedIn cookies typically expire after 30 days
   - Make sure only one session uses the same cookie

2. **Function timeout errors**:
   - Default timeout is 5 minutes
   - Browser initialization can take 10-30 seconds on cold start
   - Consider using **Premium plan** for better performance

3. **Memory issues**:
   - Chrome browser requires significant memory
   - Monitor memory usage in Application Insights
   - Consider upgrading to **Premium plan** for more memory

### Debug Locally

```bash
# Enable debug logging
export LINKEDIN_MCP_LOG_LEVEL=DEBUG

# Run with development storage
func start
```

### View Azure Logs

```bash
# Stream live logs
func azure functionapp logstream linkedin-mcp-server

# Or view in Azure portal under Monitor > Logs
```

## Migration from Docker

This Azure Functions implementation replaces the Docker deployment method. Key differences:

- **No Docker required**: Runs directly on Azure Functions runtime
- **Serverless scaling**: Automatically scales based on demand  
- **Pay-per-use**: Only pay for actual function executions
- **Integrated monitoring**: Built-in Azure Application Insights
- **Managed infrastructure**: No server management required

The API remains compatible with the original MCP server implementation.