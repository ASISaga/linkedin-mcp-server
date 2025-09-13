#!/bin/bash

# Azure Functions Deployment Script for LinkedIn MCP Server
# This script automates the deployment of the LinkedIn MCP Server to Azure Functions

set -e  # Exit on any error

echo "🚀 LinkedIn MCP Server - Azure Functions Deployment"
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install Azure CLI first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Functions Core Tools is installed
if ! command -v func &> /dev/null; then
    echo "❌ Azure Functions Core Tools not found. Please install it first:"
    echo "   npm install -g azure-functions-core-tools@4 --unsafe-perm true"
    exit 1
fi

# Check if user is logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please login to Azure..."
    az login
fi

# Get current subscription info
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "📋 Using Azure subscription: $SUBSCRIPTION_NAME"

# Prompt for deployment configuration
read -p "📝 Enter resource group name (default: linkedin-mcp-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-linkedin-mcp-rg}

read -p "📝 Enter function app name (must be globally unique): " FUNCTION_APP_NAME
if [[ -z "$FUNCTION_APP_NAME" ]]; then
    echo "❌ Function app name is required"
    exit 1
fi

read -p "📝 Enter Azure region (default: East US): " LOCATION
LOCATION=${LOCATION:-"East US"}

read -p "🍪 Enter your LinkedIn cookie (li_at value): " LINKEDIN_COOKIE
if [[ -z "$LINKEDIN_COOKIE" ]]; then
    echo "❌ LinkedIn cookie is required"
    exit 1
fi

read -p "📊 Enter log level (DEBUG/INFO/WARNING/ERROR, default: WARNING): " LOG_LEVEL
LOG_LEVEL=${LOG_LEVEL:-WARNING}

echo ""
echo "🔧 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Function App: $FUNCTION_APP_NAME"
echo "   Location: $LOCATION"
echo "   Log Level: $LOG_LEVEL"
echo ""

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo "🏗️  Creating Azure resources..."

# Create resource group
echo "📦 Creating resource group: $RESOURCE_GROUP"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

# Generate unique storage account name
STORAGE_ACCOUNT="${FUNCTION_APP_NAME}storage"
STORAGE_ACCOUNT=$(echo "$STORAGE_ACCOUNT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g' | cut -c1-24)

# Create storage account
echo "💾 Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
    --name "$STORAGE_ACCOUNT" \
    --location "$LOCATION" \
    --resource-group "$RESOURCE_GROUP" \
    --sku Standard_LRS \
    --output none

# Create function app
echo "⚡ Creating function app: $FUNCTION_APP_NAME"
az functionapp create \
    --resource-group "$RESOURCE_GROUP" \
    --consumption-plan-location "$LOCATION" \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --name "$FUNCTION_APP_NAME" \
    --storage-account "$STORAGE_ACCOUNT" \
    --output none

echo "🔧 Configuring environment variables..."

# Set environment variables
az functionapp config appsettings set \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        LINKEDIN_COOKIE="$LINKEDIN_COOKIE" \
        LINKEDIN_MCP_LOG_LEVEL="$LOG_LEVEL" \
        LINKEDIN_MCP_HEADLESS="1" \
        LINKEDIN_MCP_LAZY_INIT="1" \
        LINKEDIN_MCP_NON_INTERACTIVE="1" \
        LINKEDIN_MCP_TRANSPORT="streamable-http" \
    --output none

echo "📦 Deploying function code..."

# Deploy the function
func azure functionapp publish "$FUNCTION_APP_NAME" --python

# Get the function URL
FUNCTION_URL="https://${FUNCTION_APP_NAME}.azurewebsites.net"

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🔗 Function URLs:"
echo "   Health Check: $FUNCTION_URL/api/health"
echo "   MCP Endpoint: $FUNCTION_URL/api/mcp"
echo ""
echo "🧪 Test the deployment:"
echo "   curl $FUNCTION_URL/api/health"
echo ""
echo "📊 Monitor your function:"
echo "   az functionapp logs tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🎉 Your LinkedIn MCP Server is now running on Azure Functions!"

# Test the health endpoint
echo "🩺 Testing health endpoint..."
sleep 10  # Wait for deployment to be ready

if curl -f -s "$FUNCTION_URL/api/health" > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. The function might still be starting up."
    echo "   Try testing manually in a few minutes."
fi