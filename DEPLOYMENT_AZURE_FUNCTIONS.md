# LinkedIn MCP Server Azure Functions Deployment

This folder is now ready to be deployed as an Azure Function App.

**Deployment Steps:**
1. Ensure you have the Azure Functions Core Tools and Azure CLI installed.
2. From this directory, run:
   ```pwsh
   func azure functionapp publish <YourFunctionAppName>
   ```
3. Set any required environment variables in Azure Portal or via `local.settings.json`.

**Structure:**
- `linkedin_mcp_server/` contains the function code and entry point (`__init__.py`).
- `function.json` defines the HTTP trigger binding.
- `host.json` and `local.settings.json` are for Azure Functions configuration.
- Dependencies are managed via `requirements.txt` and `pyproject.toml`.

**Note:**
- Make sure all dependencies are included in `requirements.txt` for Azure Functions deployment.
- You may need to adjust the entry point or handler if your server logic changes.
