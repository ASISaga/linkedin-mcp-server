// azure/bicep/modules/function.bicep
// Azure Functions Flexible Consumption plan module.
//
// Key Flex Consumption characteristics provisioned here:
//   - Scale-to-zero by default (0 idle instances, wake on trigger)
//   - HTTP trigger wakes the app on incoming MCP requests
//   - Service Bus trigger wakes the app on queue messages
//   - System-assigned managed identity (principle of least privilege)
//   - Deployment via blob-stored ZIP package (Flex Consumption requirement)
//
// NOTE: Flex Consumption requires NO Microsoft.Web/serverfarms resource.
//       Billing is per-execution (consumption model).

@description('Application name prefix.')
param appName string

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

@description('Storage account name for AzureWebJobsStorage.')
param storageAccountName string

@description('Storage account connection string.')
@secure()
param storageConnectionString string

@description('URL of the deployment package blob container.')
param deploymentContainerUrl string

@description('Application Insights connection string.')
@secure()
param appInsightsConnectionString string

@description('Service Bus connection string.')
@secure()
param serviceBusConnectionString string

@description('Service Bus queue name.')
param serviceBusQueueName string = 'mcp-requests'

@description('Maximum concurrent function instances.')
param maxInstances int = 100

@description('Instance memory in MB (512 | 1024 | 2048 | 4096).')
param instanceMemoryMb int = 2048

@description(
  'Concurrent HTTP requests per instance before scaling out. '
  'Lower values (4-8) favour responsiveness; higher (16-32) favour throughput. '
  'Default 16 balances MCP workloads that are primarily I/O-bound.'
)
param httpConcurrencyPerInstance int = 16

@description('LinkedIn OAuth client ID.')
@secure()
param linkedInClientId string = ''

@description('LinkedIn OAuth client secret.')
@secure()
param linkedInClientSecret string = ''

@description('LinkedIn pre-issued access token.')
@secure()
param linkedInAccessToken string = ''

// ---------------------------------------------------------------------------
// Function app – Flex Consumption
// ---------------------------------------------------------------------------

var functionAppName = '${appName}-fn'

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    // Flex Consumption configuration block
    functionAppConfig: {
      deployment: {
        storage: {
          // Deployment packages are stored as ZIP blobs in this container
          type: 'blobContainer'
          value: deploymentContainerUrl
          authentication: {
            type: 'StorageAccountConnectionString'
            storageAccountConnectionStringName: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          }
        }
      }
      scaleAndConcurrency: {
        // Scale-to-zero: minimum 0 instances when idle
        maximumInstanceCount: maxInstances
        instanceMemoryMB: instanceMemoryMb
        triggers: {
          http: {
            // Configurable: lower = faster scale-out, higher = better utilisation
            perInstanceConcurrency: httpConcurrencyPerInstance
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.12'
      }
    }
    siteConfig: {
      appSettings: [
        // --- Azure Functions runtime ---
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
        }
        {
          name: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          value: storageConnectionString
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        // --- Observability ---
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        // --- Service Bus trigger ---
        {
          name: 'SERVICE_BUS_CONNECTION_STRING'
          value: serviceBusConnectionString
        }
        {
          name: 'SERVICE_BUS_QUEUE_NAME'
          value: serviceBusQueueName
        }
        // --- LinkedIn OAuth ---
        {
          name: 'LINKEDIN_CLIENT_ID'
          value: linkedInClientId
        }
        {
          name: 'LINKEDIN_CLIENT_SECRET'
          value: linkedInClientSecret
        }
        {
          name: 'LINKEDIN_ACCESS_TOKEN'
          value: linkedInAccessToken
        }
        // --- Server behaviour ---
        {
          name: 'LINKEDIN_MCP_NON_INTERACTIVE'
          value: '1'
        }
        {
          name: 'LINKEDIN_MCP_LOG_LEVEL'
          value: 'WARNING'
        }
      ]
      // Linux consumption plan requires Python 3.12+
      linuxFxVersion: 'Python|3.12'
    }
    // HTTPS-only; no plain-HTTP fallback
    httpsOnly: true
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Function app resource name.')
output functionAppName string = functionApp.name

@description('Default hostname (without https://).')
output defaultHostname string = functionApp.properties.defaultHostName

@description('System-assigned managed identity principal ID.')
output principalId string = functionApp.identity.principalId
