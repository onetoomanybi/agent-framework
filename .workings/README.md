# Microsoft Fabric + Azure AI Foundry Integration

This project enables bidirectional integration between Microsoft Fabric and Azure AI Foundry agents, allowing agents to read and process files from Fabric Lakehouses.

## Architecture Overview

```
┌─────────────────────────┐
│  Fabric Notebook        │
│  (Your Code)            │
│  ┌──────────────────┐   │
│  │ FabricMLCredential│   │
│  │ AIProjectClient  │   │
│  └──────────────────┘   │
└───────────┬─────────────┘
            │ Authentication (ml.azure.com scope)
            │
            ▼
┌─────────────────────────┐
│  Azure AI Foundry       │
│  Agent Service          │
│  ┌──────────────────┐   │
│  │  Agent + Tools   │   │
│  │  (OpenAPI)       │   │
│  └──────────────────┘   │
└───────────┬─────────────┘
            │ Authentication (powerbi/api scope)
            │
            ▼
┌─────────────────────────┐
│  Fabric Lakehouse       │
│  (OneLake Storage)      │
│  ┌──────────────────┐   │
│  │  CSV Files       │   │
│  │  Data            │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

## Components

### 1. Fabric Client (`fabric_ai_foundry_client.py`)
- Runs in Microsoft Fabric notebooks
- Uses `FabricMLCredential` for authentication
- Connects to Azure AI Foundry agents
- Creates conversation threads and processes responses

### 2. Agent Tools (`agent_lakehouse_tools.py`)
- Runs in Azure AI Foundry as agent tool implementations
- Provides three main functions:
  - `listFiles`: List files in a lakehouse
  - `readCSVFile`: Read and parse CSV files
  - `getLakehouseInfo`: Get lakehouse metadata
- Uses `FabricLakehouseCredential` for Fabric authentication

### 3. OpenAPI Specification (`openapi_spec.json`)
- Defines the agent tools as API endpoints
- Used by Azure AI Foundry to understand tool capabilities
- Maps operations to function implementations

## Setup Instructions

### Prerequisites

1. **Microsoft Fabric Workspace** with a Lakehouse
2. **Azure AI Foundry Project** with agent capabilities
3. **Azure Function App** (or similar) to host agent tools
4. **Proper permissions configured** (see Permissions section)

### Step 1: Install Dependencies

In your Fabric notebook:
```python
%pip install azure-ai-projects azure-identity azure-storage-file-datalake
```

### Step 2: Configure Fabric Client

1. Update the configuration in `fabric_ai_foundry_client.py`:
   ```python
   ENDPOINT = "https://your-project.services.ai.azure.com"
   AGENT_ID = "asst_YourAgentID"
   ```

2. Run the client code in your Fabric notebook

### Step 3: Deploy Agent Tools

1. Deploy `agent_lakehouse_tools.py` to an Azure Function App
2. Ensure the Function App has:
   - Managed Identity enabled
   - Permissions to access Fabric (see Permissions)

### Step 4: Register Tools in AI Foundry

1. Go to your Azure AI Foundry project
2. Create or edit your agent
3. Add tools using the OpenAPI specification:
   - Upload `openapi_spec.json`
   - Configure the server URL to point to your Function App
   - Map operations to your deployed functions

## Permissions Setup

### Fabric → AI Foundry (Client Side)

The Fabric workspace identity needs:
- Permission to call Azure AI Foundry API
- Scope: `https://ml.azure.com`

This is handled automatically by `notebookutils.credentials.getToken()`

### AI Foundry → Fabric (Agent Tools Side)

The Function App's managed identity needs:
1. **Fabric permissions**:
   - Reader role on the Fabric workspace
   - Access to the specific lakehouse
   
2. **Configure in Fabric**:
   - Go to Workspace settings
   - Add the Function App's managed identity
   - Grant appropriate permissions

3. **Azure AD token scope**:
   - `https://analysis.windows.net/powerbi/api/.default`

## Usage Examples

### Example 1: List CSV Files

```python
from fabric_ai_foundry_client import connect_to_ai_foundry, run_agent_conversation

# Configuration
ENDPOINT = "https://your-project.services.ai.azure.com"
AGENT_ID = "asst_YourAgentID"

# Connect
client, agent = connect_to_ai_foundry(ENDPOINT, AGENT_ID)

# Ask agent to list CSV files
response = run_agent_conversation(
    client, 
    agent, 
    "List all CSV files in the lakehouse"
)

print(response)
```

### Example 2: Read Specific CSV File

```python
response = run_agent_conversation(
    client,
    agent,
    "Read the sales.csv file from the Files folder"
)

print(response)
```

### Example 3: Get Lakehouse Info

```python
response = run_agent_conversation(
    client,
    agent,
    "What information can you tell me about my lakehouse?"
)

print(response)
```

## Authentication Flows

### Flow 1: Fabric → AI Foundry

```python
# In Fabric notebook
token = notebookutils.credentials.getToken("https://ml.azure.com")
# → Used by FabricMLCredential
# → Authenticates AIProjectClient
# → Allows agent calls
```

### Flow 2: AI Foundry → Fabric

```python
# In agent tool
credential = DefaultAzureCredential()  # Uses managed identity
token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
# → Used by FabricLakehouseCredential
# → Authenticates DataLakeServiceClient
# → Allows OneLake access
```

## Troubleshooting

### Issue: Authentication fails from Fabric

**Solution**: Ensure you're using the correct scope:
```python
token = notebookutils.credentials.getToken("https://ml.azure.com")
```

### Issue: Agent can't access Lakehouse

**Solution**: Check permissions:
1. Verify Function App has managed identity
2. Check Fabric workspace permissions
3. Confirm identity has Reader role

### Issue: Timeouts when calling agent

**Possible causes**:
- Agent tools are slow to respond
- Authentication is taking too long
- Network connectivity issues

**Solutions**:
- Increase timeout settings
- Check agent tool logs
- Verify Function App is running

### Issue: CSV file not found

**Solution**: Verify the path format:
- Use forward slashes: `Files/data/file.csv`
- Include lakehouse ID in the path
- Check file actually exists in OneLake

## File Structure

```
.
├── fabric_ai_foundry_client.py   # Client code for Fabric notebooks
├── agent_lakehouse_tools.py      # Agent tool implementations
├── openapi_spec.json             # OpenAPI specification for tools
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Security Considerations

1. **Token Expiration**: Tokens expire after 1 hour. The code handles this automatically.

2. **Managed Identity**: Always use managed identity in production. Avoid storing credentials.

3. **Least Privilege**: Grant only necessary permissions to identities.

4. **Data Access**: Implement appropriate access controls in your agent logic.

## Next Steps

1. **Error Handling**: Add more robust error handling for production use
2. **Logging**: Implement comprehensive logging for debugging
3. **Caching**: Consider caching frequently accessed files
4. **Pagination**: Implement pagination for large file lists
5. **Data Processing**: Add more advanced CSV processing capabilities

## References

- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [OneLake Documentation](https://learn.microsoft.com/en-us/fabric/onelake/)
- [Azure AI Agents SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Azure AI Foundry logs
3. Check Function App logs
4. Verify permissions in Fabric workspace
