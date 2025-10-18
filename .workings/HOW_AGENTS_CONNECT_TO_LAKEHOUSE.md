# How Agents Connect to the Lakehouse - Complete Breakdown

## THE BIG PICTURE

```
User in Fabric          Azure AI Foundry         Azure Function         Fabric Lakehouse
    │                        │                         │                       │
    │                        │                         │                       │
    ├─ "Find files"         │                         │                       │
    │─────────────────────→ │                         │                       │
    │                        │                         │                       │
    │                        ├─ Need data! ──────────→│                       │
    │                        │                         │                       │
    │                        │                         ├─ Connect ────────────→│
    │                        │                         │  (with token)         │
    │                        │                         │                       │
    │                        │                    ←────│── Here are files ────│
    │                        │                         │                       │
    │                   ←────│────────────────────────│                       │
    │                        │                         │                       │
    │ ← Response ────────────│                         │                       │
```

---

## CONNECTION LAYERS (THREE-STEP PROCESS)

### LAYER 1: Fabric Notebook → Azure AI Foundry
**Where**: User's Fabric notebook
**How**: Using Fabric's built-in credentials

```python
class FabricMLCredential:
    def get_token(self, *scopes, **kwargs):
        # Fabric gives us a token for ml.azure.com
        token = notebookutils.credentials.getToken("https://ml.azure.com")
        
        # Create token object
        return type('TokenInfo', (), {
            'token': token,
            'expires_on': expiration_time
        })()
```

**What happens**:
1. User runs code in Fabric notebook
2. Code calls `notebookutils.credentials.getToken()`
3. Fabric's infrastructure provides a token
4. Token is scoped for Azure AI Foundry access (`ml.azure.com`)
5. Token is passed to AIProjectClient

**Authentication Flow**:
```
Fabric Notebook
    │
    ├─ notebookutils.credentials
    │  (built-in to Fabric)
    │
    └─→ Get token for ml.azure.com
        └─→ Returns JWT token
            └─→ Valid for 1 hour
                └─→ Used by AIProjectClient
```

---

### LAYER 2: Azure AI Foundry → Azure Function
**Where**: Azure AI Foundry agent execution
**How**: Using OpenAPI specification

```json
{
  "servers": [
    {
      "url": "https://your-function-app.azurewebsites.net/api"
    }
  ],
  "paths": {
    "/listFiles": {
      "post": {
        "operationId": "listFiles",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "workspace_id": {"type": "string"},
                  "lakehouse_id": {"type": "string"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**What happens**:
1. Agent needs data from lakehouse
2. Looks at OpenAPI spec for available tools
3. Determines which tool to call (e.g., listFiles)
4. Makes HTTP POST request to Azure Function
5. Includes workspace_id and lakehouse_id in request body
6. Azure Function returns JSON response

**Request Flow**:
```
Agent decision: "User wants files"
    │
    ├─ Check OpenAPI spec
    │ "I can use listFiles tool"
    │
    ├─ Prepare HTTP request
    │ POST /api/listFiles
    │ Body: {workspace_id: "xyz", lakehouse_id: "abc"}
    │
    └─→ Send to Azure Function
        └─→ Azure Function processes
            └─→ Returns JSON with files
```

---

### LAYER 3: Azure Function → Fabric Lakehouse
**Where**: Azure Function runtime
**How**: Using Managed Identity + OneLake connection

```python
async def list_lakehouse_files(workspace_id, lakehouse_id, path="Files"):
    # Step 1: Create credential
    credential = FabricLakehouseCredential()
    
    # Step 2: Get token for Power BI/API scope
    token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
    
    # Step 3: Connect to OneLake
    datalake_client = DataLakeServiceClient(
        account_url="https://onelake.dfs.fabric.microsoft.com",
        credential=credential
    )
    
    # Step 4: Get file system client
    fs_client = datalake_client.get_file_system_client(workspace_id)
    
    # Step 5: List paths in lakehouse
    paths = fs_client.get_paths(path=f"{lakehouse_id}/Files")
    
    # Step 6: Extract files and return
    files = [...]
    return json.dumps({"success": True, "files": files})
```

**What happens**:
1. Azure Function receives request
2. Creates FabricLakehouseCredential
3. Credential uses DefaultAzureCredential (Managed Identity)
4. Gets token with `powerbi/api` scope
5. Connects to OneLake (Fabric's data lake storage)
6. Uses workspace_id as file system name
7. Lists files in lakehouse folder
8. Returns file list

**Authentication Flow**:
```
Azure Function receives request
    │
    ├─ Create FabricLakehouseCredential
    │
    ├─ Call DefaultAzureCredential
    │ (Managed Identity from Azure)
    │
    ├─ Get token for powerbi/api scope
    │ (Token signed by Azure AD)
    │
    ├─ Connect to OneLake
    │ account_url = "https://onelake.dfs.fabric.microsoft.com"
    │
    ├─ Access file system
    │ fs_name = workspace_id
    │
    ├─ List files
    │ path = lakehouse_id/Files
    │
    └─→ Return results
```

---

## THE FULL REQUEST JOURNEY

### User asks: "What files do I have?"

#### STEP 1: Fabric → AI Foundry (with ml.azure.com token)
```
Location: Fabric Notebook
Code runs:
  credential = FabricMLCredential()
  client = AIProjectClient(endpoint=endpoint, credential=credential)
  agent = client.agents.get_agent(agent_id)
  thread = client.agents.create_thread()
  client.agents.create_message(thread_id, role="user", content="What files do I have?")
  run = client.agents.create_and_process_run(thread_id, agent_id)

Token: ml.azure.com scope (from Fabric's notebookutils)
Connection: HTTPS to Azure AI Foundry
Result: Agent receives the user message
```

#### STEP 2: AI Foundry decides to call tool
```
Location: Azure AI Foundry execution environment
Agent thinks: "User wants files, I should call listFiles tool"

Decision made based on:
  - OpenAPI specification defines listFiles
  - User question matches tool purpose
  - No other tool is more appropriate

Next: Make HTTP request to Azure Function
```

#### STEP 3: AI Foundry → Azure Function (HTTPS POST)
```
Location: Network request from AI Foundry to Azure Function
Request:
  POST https://your-function-app.azurewebsites.net/api/listFiles
  Content-Type: application/json
  Authorization: <function key or managed identity token>
  
  {
    "workspace_id": "abc-123-def-456",
    "lakehouse_id": "xyz-789-uvw-012",
    "path": "Files"
  }

Response: 
  200 OK
  {
    "success": true,
    "file_count": 3,
    "files": [
      {"name": "sales.csv", "size": 1024000, "last_modified": "2025-10-18T10:30:00"},
      {"name": "customers.csv", "size": 2048000, "last_modified": "2025-10-18T11:00:00"},
      {"name": "inventory.csv", "size": 512000, "last_modified": "2025-10-18T09:15:00"}
    ]
  }
```

#### STEP 4: Azure Function → OneLake (with powerbi/api token)
```
Location: Inside Azure Function
Code runs:
  credential = FabricLakehouseCredential()
  token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
  
  datalake_client = DataLakeServiceClient(
    account_url="https://onelake.dfs.fabric.microsoft.com",
    credential=credential
  )
  
  fs_client = datalake_client.get_file_system_client("abc-123-def-456")
  paths = fs_client.get_paths(path="xyz-789-uvw-012/Files")

Token: powerbi/api scope (from Managed Identity)
Connection: HTTPS to OneLake storage endpoint
Result: List of files from lakehouse
```

#### STEP 5: Azure Function → AI Foundry (JSON response)
```
Location: Network response from Azure Function
Response:
  200 OK
  {
    "success": true,
    "file_count": 3,
    "files": [...]
  }

AI Foundry receives and processes:
  - Sees success: true
  - Counts 3 files
  - Prepares response for user
```

#### STEP 6: AI Foundry → Fabric (conversational response)
```
Location: Fabric Notebook
Agent response:
  "You have 3 files: sales.csv (1 MB), customers.csv (2 MB), and inventory.csv (512 KB)"

User sees: Natural language response about their files
```

---

## AUTHENTICATION BREAKDOWN

### Who authenticates with what scope?

```
┌─────────────────────────────────────────────────┐
│ AUTHENTICATION MAPPING TABLE                    │
├─────────────────────────────────────────────────┤
│ Component              │ Authenticates with     │
├────────────────────────┼────────────────────────┤
│ Fabric notebook        │ ml.azure.com scope     │
│ (via notebookutils)    │ → AIProjectClient      │
├────────────────────────┼────────────────────────┤
│ Azure Function         │ powerbi/api scope      │
│ (via Managed Identity) │ → OneLake access       │
├────────────────────────┼────────────────────────┤
│ AI Foundry agent       │ Calls via OpenAPI      │
│ (no direct auth)       │ → Uses function URL    │
└─────────────────────────────────────────────────┘
```

### Two different token scopes, why?

**ml.azure.com scope** (Fabric → AI Foundry):
- Used for Azure AI Foundry API calls
- Authenticates notebook to AI Foundry
- Limited to AI operations
- Token: 1 hour expiration

**powerbi/api scope** (Function → OneLake):
- Used for Power BI / data lake access
- Authenticates function to OneLake
- Limited to data operations
- Token: Managed by Azure Identity

---

## THE CONNECTION CHAIN VISUALIZATION

```
TRUST CHAIN:
────────────

Azure AD (Identity Provider)
│
├── Issues token for: ml.azure.com scope
│   To: Fabric notebook user
│   For: AIProjectClient
│
├── Issues token for: powerbi/api scope
│   To: Azure Function Managed Identity
│   For: OneLake DataLakeServiceClient
│

CONNECTION CHAIN:
─────────────────

Fabric Notebook
    ↓ (notebookutils.credentials + ml.azure.com token)
Azure AI Foundry
    ↓ (HTTP POST with tool call)
Azure Function
    ↓ (DefaultAzureCredential + powerbi/api token)
OneLake (Fabric Lakehouse)


DATA FLOW:
──────────

User Query
    ↓
Fabric receives
    ↓
Send to AI Foundry
    ↓
Agent thinks: "Which tool to use?"
    ↓
AI Foundry: "I need data from lakehouse"
    ↓
Azure Function: "Accessing lakehouse..."
    ↓
OneLake: "Here's the data"
    ↓
Azure Function: "Returning results"
    ↓
AI Foundry: "Processing results"
    ↓
Agent: "Formatting response"
    ↓
Fabric: "Showing to user"
    ↓
User sees answer
```

---

## WHAT HAPPENS AT EACH CONNECTION POINT

### Connection 1: Fabric → AI Foundry
**Protocol**: Azure SDK (HTTPS)
**What's sent**: 
- Authentication: JWT token (ml.azure.com scope)
- Data: User messages, thread info
- What's returned: Agent responses, tool calls

**Why separate token scopes?**
- Notebook doesn't need access to data lake
- Only needs to talk to AI Foundry
- Principle of least privilege

### Connection 2: AI Foundry → Azure Function
**Protocol**: REST API (HTTPS)
**What's sent**:
- Method: POST
- Headers: Authentication headers
- Body: JSON with workspace_id, lakehouse_id, etc.
- What's returned: JSON with file lists, CSV data, metadata

**Why OpenAPI?**
- AI agent needs to know what tools are available
- OpenAPI spec defines parameters and responses
- AI can validate its requests match spec

### Connection 3: Azure Function → OneLake
**Protocol**: Azure Storage SDK (HTTPS)
**What's sent**:
- Authentication: JWT token (powerbi/api scope)
- Queries: List paths, read files
- What's returned: File lists, file contents

**Why separate from Fabric connection?**
- Azure Function needs different permissions
- Uses Managed Identity (no hardcoded secrets)
- OneLake is separate storage service

---

## CREDENTIALS IN THIS SYSTEM

### Credential 1: Fabric's notebookutils
```python
# In Fabric notebook
token = notebookutils.credentials.getToken("https://ml.azure.com")

How it works:
- Built into Fabric environment
- Automatically gets user's token
- No code needed to set credentials
- User's identity used throughout
```

### Credential 2: Azure Managed Identity
```python
# In Azure Function
cred = DefaultAzureCredential()

How it works:
- Function app has Managed Identity assigned
- Azure AD automatically provides token
- No stored credentials
- Secure by design
- Must give Function app RBAC permissions
```

### No hardcoded secrets!
```
❌ Bad:
password = "SecretPassword123"

✅ Good (this system):
Credentials come from Azure infrastructure
```

---

## PUTTING IT TOGETHER: THE CONNECTION CHECKLIST

For agents to successfully connect to lakehouse:

```
FABRIC NOTEBOOK SIDE:
✓ Running in Fabric workspace
✓ Has access to notebookutils
✓ Can call notebookutils.credentials.getToken()
✓ User has permission to use AI Foundry

AZURE AI FOUNDRY SIDE:
✓ Agent created with proper instructions
✓ OpenAPI spec configured with correct server URL
✓ Agent has read the OpenAPI spec

AZURE FUNCTION SIDE:
✓ Deployed to Azure
✓ Has Managed Identity assigned
✓ Function app has RBAC access to OneLake
✓ Code imports DataLakeServiceClient
✓ Endpoints match OpenAPI spec

FABRIC LAKEHOUSE SIDE:
✓ Lakehouse exists in Fabric
✓ Workspace ID known
✓ Lakehouse ID known
✓ Files or CSV data exist
✓ Function's Managed Identity has read access

NETWORK SIDE:
✓ Function app URL is accessible from AI Foundry
✓ OneLake endpoint is accessible
✓ No firewall blocking connections
✓ SSL/TLS certificates valid
```

---

## REAL-WORLD EXAMPLE: TRACING A FILE READ

### User: "Show me the first 5 rows of sales.csv"

```
TIME: T+0ms
Location: Fabric Notebook
Action: User clicks "Run" or presses Shift+Enter
Code runs:
  run_agent_conversation(client, agent, "Show me the first 5 rows of sales.csv")

TIME: T+50ms
Location: Fabric Notebook
Action: Code creates thread and sends message
Code runs:
  thread = client.agents.create_thread()
  client.agents.create_message(thread_id, role="user", content="...")
  run = client.agents.create_and_process_run(thread_id, agent_id)

Time: T+100ms
Location: Azure AI Foundry
Action: Agent receives message and decides what to do
Thinking:
  1. User wants to see rows from "sales.csv"
  2. Need to use readCSVFile tool
  3. Need workspace_id and lakehouse_id
  4. Need file_path = "sales.csv"
Agent prepares tool call

TIME: T+150ms
Location: Azure AI Foundry
Action: Agent calls tool via HTTP
Request sent:
  POST https://your-function-app.azurewebsites.net/api/readCSVFile
  Content-Type: application/json
  {
    "workspace_id": "abc-123-def-456",
    "lakehouse_id": "xyz-789-uvw-012",
    "file_path": "sales.csv"
  }

TIME: T+200ms
Location: Azure Function (listFiles endpoint)
Action: Function receives request
Code runs:
  req_body = req.get_json()
  workspace_id = req_body.get('workspace_id')
  lakehouse_id = req_body.get('lakehouse_id')
  file_path = req_body.get('file_path')
  result = await read_csv_file(workspace_id, lakehouse_id, file_path)

TIME: T+250ms
Location: Azure Function (inside read_csv_file)
Action: Creating connection to OneLake
Code runs:
  credential = FabricLakehouseCredential()
  datalake_client = DataLakeServiceClient(
    account_url="https://onelake.dfs.fabric.microsoft.com",
    credential=credential
  )

TIME: T+300ms
Location: Azure AD
Action: Issuing token
Azure AD sees:
  - Request from Azure Function
  - Function has Managed Identity
  - Scope: powerbi/api
  - Issues token

TIME: T+350ms
Location: OneLake
Action: Receiving connection with token
OneLake sees:
  - Valid token from Azure AD
  - Function's Managed Identity
  - Grants access

TIME: T+400ms
Location: OneLake
Action: Function lists and opens file
OneLake returns:
  - File handle to sales.csv
  - File contents

TIME: T+450ms
Location: Azure Function (read_csv_file)
Action: Parsing CSV
Code runs:
  file_client = fs_client.get_file_client(file_path)
  download = file_client.download_file()
  content = download.readall().decode('utf-8')
  Parse CSV, take first 5 rows

TIME: T+500ms
Location: Azure Function
Action: Sending response back
Returns:
  {
    "success": true,
    "row_count": 1000,
    "headers": ["date", "product", "quantity", "price"],
    "data": [
      {"date": "2025-10-01", "product": "Widget A", "quantity": "100", "price": "9.99"},
      {"date": "2025-10-01", "product": "Widget B", "quantity": "50", "price": "19.99"},
      ...
    ]
  }

TIME: T+550ms
Location: Azure AI Foundry
Action: Agent receives results
Agent sees:
  - File has 1000 rows
  - Headers: date, product, quantity, price
  - First 5 rows of data
  - All successful

TIME: T+600ms
Location: Azure AI Foundry
Action: Agent formats response
Response created:
  "I found sales.csv with 1,000 total rows. Here are the first 5 rows:
   - Date: 2025-10-01, Product: Widget A, Quantity: 100, Price: $9.99
   - Date: 2025-10-01, Product: Widget B, Quantity: 50, Price: $19.99
   ..."

TIME: T+650ms
Location: Fabric Notebook
Action: User sees response
Display:
  "I found sales.csv with 1,000 total rows. Here are the first 5 rows:
   ..."

TOTAL TIME: ~650ms
```

---

## SUMMARY: HOW AGENTS CONNECT TO LAKEHOUSE

```
The connection happens in THREE AUTHENTICATED HOPS:

1. FABRIC NOTEBOOK
   - Uses notebookutils.credentials
   - Gets ml.azure.com scope token
   - Connects to AIProjectClient
   └─→ Sends user query to agent

2. AZURE AI FOUNDRY
   - Agent reads OpenAPI spec
   - Decides which tool to call
   - Makes HTTP POST to Azure Function
   └─→ Sends tool request with workspace/lakehouse IDs

3. AZURE FUNCTION → ONELAKE
   - Uses Managed Identity
   - Gets powerbi/api scope token
   - Connects to OneLake via DataLakeServiceClient
   - Reads files from lakehouse
   └─→ Returns data back to agent

Result: User gets conversational answer about their data
```

**Key Points**:
- ✅ No hardcoded credentials anywhere
- ✅ Each component has minimal permissions (least privilege)
- ✅ Different token scopes for different jobs
- ✅ Managed Identity for Azure services
- ✅ Fabric's notebookutils for user authentication
- ✅ OpenAPI spec defines the contract between Agent and Function
- ✅ All communication is HTTPS encrypted
