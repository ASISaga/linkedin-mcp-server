// azure/bicep/modules/storage.bicep
// Storage account module.
//
// Provisions a storage account with:
//   - A blob container for the Flex Consumption deployment package
//   - Standard redundancy (LRS) – sufficient for function state

@description('Application name prefix.')
param appName string

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

// Storage account names: 3-24 chars, lowercase alphanumeric only
var storageAccountName = take(toLower(replace(replace('${appName}st', '-', ''), '_', '')), 24)
var deploymentContainerName = 'deploymentpackage'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource deploymentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: deploymentContainerName
  properties: {
    publicAccess: 'None'
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Storage account name.')
output storageAccountName string = storageAccount.name

@description('Primary connection string for AzureWebJobsStorage.')
output connectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'

@description('URL of the deployment package blob container.')
output deploymentContainerUrl string = '${storageAccount.properties.primaryEndpoints.blob}${deploymentContainerName}'
