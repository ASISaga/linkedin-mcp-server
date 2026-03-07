// azure/bicep/main.bicep
// Top-level orchestration for the LinkedIn MCP Server on Azure Functions
// Flexible Consumption plan.
//
// Resources provisioned
// ---------------------
//   Storage account          - function state + Flex Consumption deployment package
//   Service Bus namespace    - async MCP request queue
//   Log Analytics workspace  - centralised logs
//   Application Insights     - telemetry + live metrics
//   Function app             - Flex Consumption (scale-to-zero, HTTP + SB triggers)

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Short name used as prefix/suffix for all resource names.')
param appName string

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Deployment environment tag.')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Maximum function instances (Flex Consumption).')
param maxInstances int = 100

@description('Memory per instance in MB (Flex Consumption: 512, 1024, 2048, 4096).')
@allowed([512, 1024, 2048, 4096])
param instanceMemoryMb int = 2048

@description('Service Bus queue name for async MCP requests.')
param serviceBusQueueName string = 'mcp-requests'

@description('LinkedIn OAuth client ID.')
@secure()
param linkedInClientId string = ''

@description('LinkedIn OAuth client secret.')
@secure()
param linkedInClientSecret string = ''

@description('LinkedIn pre-issued access token (optional).')
@secure()
param linkedInAccessToken string = ''

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------

var tags = {
  application: 'linkedin-mcp-server'
  environment: environment
  'managed-by': 'bicep'
}

// ---------------------------------------------------------------------------
// Modules
// ---------------------------------------------------------------------------

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    appName: appName
    location: location
    tags: tags
  }
}

module serviceBus 'modules/service_bus.bicep' = {
  name: 'serviceBus'
  params: {
    appName: appName
    location: location
    queueName: serviceBusQueueName
    tags: tags
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    appName: appName
    location: location
    tags: tags
  }
}

module functionApp 'modules/function.bicep' = {
  name: 'functionApp'
  params: {
    appName: appName
    location: location
    tags: tags
    storageAccountName: storage.outputs.storageAccountName
    storageConnectionString: storage.outputs.connectionString
    deploymentContainerUrl: storage.outputs.deploymentContainerUrl
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    serviceBusConnectionString: serviceBus.outputs.connectionString
    serviceBusQueueName: serviceBusQueueName
    maxInstances: maxInstances
    instanceMemoryMb: instanceMemoryMb
    linkedInClientId: linkedInClientId
    linkedInClientSecret: linkedInClientSecret
    linkedInAccessToken: linkedInAccessToken
  }
  dependsOn: [storage, serviceBus, monitoring]
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Function app default hostname.')
output functionAppHostname string = functionApp.outputs.defaultHostname

@description('MCP HTTP endpoint.')
output mcpEndpoint string = 'https://${functionApp.outputs.defaultHostname}/api/mcp'

@description('Health check endpoint.')
output healthEndpoint string = 'https://${functionApp.outputs.defaultHostname}/api/health'

@description('Service Bus queue for async requests.')
output serviceBusQueue string = serviceBus.outputs.queueName

@description('Application Insights name for monitoring.')
output appInsightsName string = monitoring.outputs.appInsightsName
