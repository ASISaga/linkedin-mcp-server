// azure/bicep/modules/monitoring.bicep
// Observability module.
//
// Provisions:
//   - Log Analytics workspace  – centralised log storage
//   - Application Insights     – function telemetry, live metrics, traces

@description('Application name prefix.')
param appName string

@description('Azure region.')
param location string

@description('Resource tags.')
param tags object = {}

var workspaceName = '${appName}-law'
var appInsightsName = '${appName}-ai'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    // Disable legacy ingestion endpoint; use workspace-based
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Application Insights connection string.')
output appInsightsConnectionString string = appInsights.properties.ConnectionString

@description('Application Insights instrumentation key (legacy).')
output instrumentationKey string = appInsights.properties.InstrumentationKey

@description('Application Insights resource name.')
output appInsightsName string = appInsights.name

@description('Log Analytics workspace ID.')
output logAnalyticsWorkspaceId string = logAnalytics.id
