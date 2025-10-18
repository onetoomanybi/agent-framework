# 🚀 Deployment & Validation Guide

## Quick Start: First Steps to Running the Code

Timeline:
- **Step 1-2 (Local Setup)**: 5-10 minutes
- **Step 3 (Deploy to Azure)**: 10-15 minutes
- **Step 4 (Configure Agent)**: 5 minutes
- **Total**: ~30-40 minutes to full deployment

---

## 📋 Step 1: Local Validation (YOUR FIRST STEP)

### What It Does

Verifies that all code is syntactically correct and dependencies are available before deployment.

### How to Do It

#### 1.1 Open Terminal in `.workings` directory

```powershell
cd C:\repo\agent-framework\.workings
```

#### 1.2 Run the validation helper

```powershell
python validation_helpers.py
```

#### 1.3 Expected Output

```
✓ Phase 1: Code validation (3/3 checks)
✓ Phase 2: Dependency analysis (4/4 checks)
✓ Phase 3: Authentication flow (3/3 checks)
✓ Phase 4: Integration patterns (3/3 checks)
✓ Phase 5: Production readiness (2/2 checks)

TOTAL: 15/15 checks passing ✓
Status: READY FOR DEPLOYMENT
```

### What to Fix If It Fails

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'azure_identity'` | Run: `pip install -r requirements.txt` |
| `SyntaxError` in `.py` file | Check the file indicated, look for missing colons or brackets |
| `ImportError` on specific module | That module is needed - run `pip install -r requirements.txt` |

---

## ✅ Step 2: Copy to Willowbrook & Verify

### 2.1 Copy validated code to Willowbrook

Copy these files from `.workings` to `willowbrook/src/`:

```powershell
# Copy from .workings to willowbrook
Copy-Item -Path C:\repo\agent-framework\.workings\agent_lakehouse_tools.py `
          -Destination C:\repo\agent-framework\willowbrook\src\
          
Copy-Item -Path C:\repo\agent-framework\.workings\fabric_ai_foundry_client.py `
          -Destination C:\repo\agent-framework\willowbrook\src\

Copy-Item -Path C:\repo\agent-framework\.workings\requirements.txt `
          -Destination C:\repo\agent-framework\willowbrook\
```

### 2.2 Verify files are in place
```powershell
ls C:\repo\agent-framework\willowbrook\src\
```

Expected output:
```
agent_lakehouse_tools.py
fabric_ai_foundry_client.py
```

---

## 🔧 Step 3: Environment Configuration

### 3.1 Copy and customize configuration

```powershell
# Copy example config
Copy-Item -Path C:\repo\agent-framework\.workings\config.example.env `
          -Destination C:\repo\agent-framework\willowbrook\.env
```

### 3.2 Edit `.env` file with your Azure details

Open `willowbrook\.env` and update these values:

```bash
# From Azure AI Foundry portal
AI_FOUNDRY_ENDPOINT=https://your-project.services.ai.azure.com
AGENT_ID=asst_YourAgentID

# From Fabric workspace settings
FABRIC_WORKSPACE_ID=12345678-1234-1234-1234-123456789012
FABRIC_LAKEHOUSE_ID=87654321-4321-4321-4321-210987654321

# Your Azure Tenant
AZURE_TENANT_ID=your-tenant-id
```

### 3.3 Validate configuration

```powershell
# Check that .env file was created
Test-Path C:\repo\agent-framework\willowbrook\.env
```

---

## ☁️ Step 4: Deploy Agent Tools to Azure

### 4.1 Create Azure Function App

#### Option A: Using Azure Portal
1. Go to Azure Portal → Create Resource → Function App
2. Set Runtime to `Python 3.11`
3. Create and note the Function App name

#### Option B: Using Azure CLI
```powershell
# Login to Azure
az login

# Create Resource Group
az group create --name willowbrook-rg --location eastus

# Create Storage Account (required for Function App)
az storage account create `
  --resource-group willowbrook-rg `
  --name willowbrookstorage `
  --location eastus

# Create Function App
az functionapp create `
  --resource-group willowbrook-rg `
  --consumption-plan-location eastus `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  --name willowbrook-agents `
  --storage-account willowbrookstorage
```

### 4.2 Deploy code to Function App

#### Option A: Using VS Code Azure Extension
1. In VS Code, press `Ctrl+Shift+P` → "Azure Functions: Deploy to Function App"
2. Select your Function App
3. Wait for deployment to complete

#### Option B: Using Azure CLI
```powershell
# From willowbrook directory
cd C:\repo\agent-framework\willowbrook

# Deploy
func azure functionapp publish willowbrook-agents
```

### 4.3 Verify deployment

```powershell
# Check function status
az functionapp show --name willowbrook-agents --resource-group willowbrook-rg

# View logs
az webapp log tail --name willowbrook-agents --resource-group willowbrook-rg
```

---

## 🔐 Step 5: Configure Permissions

### 5.1 Enable Managed Identity on Function App

```powershell
# Enable system-assigned managed identity
az functionapp identity assign `
  --name willowbrook-agents `
  --resource-group willowbrook-rg
```

### 5.2 Grant Function App Access to Fabric

This requires Azure Admin to configure in Power BI Admin Portal or through Azure AD:

1. Go to **Fabric Admin Portal** → **Tenant Settings**
2. Under "Integration settings" → Enable "Service principals can use Fabric APIs"
3. Add your Function App's Managed Identity to allowed service principals

Alternatively, use Azure CLI for RBAC:
```powershell
# Get the managed identity object ID
$objectId = az functionapp identity show `
  --name willowbrook-agents `
  --resource-group willowbrook-rg `
  --query principalId -o tsv

# Assign role (requires Fabric admin)
# This typically needs to be done through Fabric portal
```

---

## 🧪 Step 6: Test the Deployment

### 6.1 Get Function App URL

```powershell
# Get your Function App URL
$functionUrl = az functionapp show `
  --name willowbrook-agents `
  --resource-group willowbrook-rg `
  --query defaultHostName -o tsv

Write-Host "Function URL: https://$functionUrl/api"
```

### 6.2 Test the listFiles endpoint

```powershell
# Create test payload
$testPayload = @{
    workspace_id = "12345678-1234-1234-1234-123456789012"
    lakehouse_id = "87654321-4321-4321-4321-210987654321"
    path = "Files"
} | ConvertTo-Json

# Call the function
$response = Invoke-RestMethod `
  -Uri "https://$functionUrl/api/listFiles" `
  -Method Post `
  -ContentType "application/json" `
  -Body $testPayload

# Check response
$response | ConvertTo-Json
```

### Expected Success Response
```json
{
  "success": true,
  "file_count": 5,
  "files": [
    {
      "name": "sales_data.csv",
      "size": 1024,
      "last_modified": "2025-10-18T10:30:00Z"
    }
  ]
}
```

### Troubleshooting
| Status | Issue | Fix |
|--------|-------|-----|
| 401 | Authentication failed | Check managed identity and Fabric permissions |
| 403 | Access denied | Verify Function App has Fabric API permissions |
| 404 | Function not found | Check Function App deployment and endpoint URL |
| 500 | Server error | Check Function App logs: `az webapp log tail ...` |

---

## 🤖 Step 7: Register Tools in Azure AI Foundry

### 7.1 Go to Azure AI Foundry Portal

Navigate to: https://ai.azure.com → Your Project

### 7.2 Create or Edit Agent

1. Click on "Agents" (or "Chat" depending on your setup)
2. Create new or edit existing agent
3. Go to "Tools" section

### 7.3 Add OpenAPI Tool

1. Click "Add Tool" → "OpenAPI"
2. Upload `willowbrook/spec/openapi_spec.json`
3. In "Server URL" field, enter:
   ```
   https://willowbrook-agents.azurewebsites.net/api
   ```
4. Save

### 7.4 Test Agent with Tools

1. Open the agent chat interface
2. Ask something like: "What files are in our lakehouse?"
3. Watch the agent call your tool and return results

---

## 📚 Step 8: Use in Fabric Notebook

### 8.1 In your Fabric Notebook, install dependencies

```python
%pip install azure-ai-projects azure-identity azure-storage-file-datalake
```

### 8.2 Load your client code

```python
# Copy the contents of fabric_ai_foundry_client.py into a cell
# Update the configuration at the top:

ENDPOINT = "https://your-project.services.ai.azure.com"
AGENT_ID = "asst_YourAgentID"
FABRIC_WORKSPACE_ID = "12345678-1234-1234-1234-123456789012"
FABRIC_LAKEHOUSE_ID = "87654321-4321-4321-4321-210987654321"
```

### 8.3 Run a test

```python
# This will create a conversation with your agent
client = AIProjectClient.from_connection_string(
    conn_str=AZURE_AI_FOUNDRY_CONN_STRING
)

# The agent can now use your tools!
```

---

## ✨ Complete Validation Checklist

After all steps, verify everything works:

- [ ] **Step 1**: `python validation_helpers.py` shows 15/15 ✓
- [ ] **Step 2**: Files copied to `willowbrook/src/` successfully
- [ ] **Step 3**: `.env` file created with all required values
- [ ] **Step 4**: Function App deployed and running
- [ ] **Step 5**: Managed Identity enabled with Fabric permissions
- [ ] **Step 6**: Test API call returns successful response
- [ ] **Step 7**: Tools registered in Azure AI Foundry
- [ ] **Step 8**: Fabric notebook can call the agent

**Status**: When all boxes are checked ✅, your deployment is complete!

---

## 🔄 Troubleshooting Quick Reference

### Problem: Validation fails
```powershell
# Reinstall all dependencies
pip install --upgrade -r requirements.txt

# Re-run validation
python validation_helpers.py
```

### Problem: Function App won't deploy
```powershell
# Check logs
az webapp log tail --name willowbrook-agents --resource-group willowbrook-rg

# Redeploy
func azure functionapp publish willowbrook-agents --build remote
```

### Problem: Agent tools not accessible
```powershell
# Test the endpoint
curl "https://willowbrook-agents.azurewebsites.net/api/listFiles" `
  -X POST `
  -H "Content-Type: application/json" `
  -d @test_payload.json
```

### Problem: "Access denied" errors
1. Verify Managed Identity is enabled: `az functionapp identity show --name willowbrook-agents --resource-group willowbrook-rg`
2. Verify Fabric workspace allows service principals
3. Check Azure AD role assignments

---

## 📞 Support Resources

- **Azure AI Foundry**: https://ai.azure.com
- **Fabric Documentation**: https://learn.microsoft.com/fabric
- **Azure Functions**: https://learn.microsoft.com/azure/azure-functions
- **Azure CLI**: `az functionapp --help`

---

**Created**: October 18, 2025  
**Status**: Ready for Deployment ✓
