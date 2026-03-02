// azure/bicep/modules/service_bus.bicep
// Azure Service Bus module.
//
// Provisions:
//   - Service Bus namespace  (Standard tier – required for queues)
//   - A single queue for incoming async MCP requests
//
// The function app's Service Bus trigger wakes the Flex Consumption instance
// when a message arrives in the queue, enabling scale-to-zero operation.

@description('Application name prefix.')
param appName string

@description('Azure region.')
param location string

@description('Queue name for async MCP requests.')
param queueName string = 'mcp-requests'

@description('Resource tags.')
param tags object = {}

var namespaceName = '${appName}-sb'

resource namespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: namespaceName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

resource queue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: namespace
  name: queueName
  properties: {
    // Retry up to 10 times before dead-lettering
    maxDeliveryCount: 10
    // Lock messages for 5 min while the function processes them
    lockDuration: 'PT5M'
    // Messages expire after 1 day if not consumed
    defaultMessageTimeToLive: 'P1D'
    deadLetteringOnMessageExpiration: true
  }
}

// Shared-access policy for the function app – Send + Listen only (principle of least privilege)
resource sendListenRule 'Microsoft.ServiceBus/namespaces/authorizationRules@2022-10-01-preview' = {
  parent: namespace
  name: 'FunctionAppAccessKey'
  properties: {
    rights: ['Send', 'Listen']
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Service Bus namespace name.')
output namespaceName string = namespace.name

@description('Queue name.')
output queueName string = queue.name

@description('Connection string for the function app.')
output connectionString string = sendListenRule.listKeys().primaryConnectionString
