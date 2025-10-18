# Microsoft Fabric + Azure AI Foundry Integration

## 📋 PROJECT PURPOSE

**Goal**: Enable Azure AI Agents to read and process files from Microsoft Fabric Lakehouses

**Use Case**: 
- Run AI agents in Azure AI Foundry
- Agents need to access data in Fabric Lakehouses
- Agents can list, read, and analyze CSV files
- Bidirectional communication between Fabric and AI Foundry

---

## 🏗️ ARCHITECTURE OVERVIEW

### Three Components

```
1. FABRIC NOTEBOOK (End User)
   └─ Runs AI agent conversation
   
2. AZURE AI FOUNDRY (Agent Service)
   └─ Hosts AI agent + tools definition
   
3. AZURE FUNCTIONS (Tool Implementation)
   └─ Implements file operations
   
4. FABRIC LAKEHOUSE (Storage)
   └─ Stores CSV and data files
```

---

## 📊 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER IN FABRIC NOTEBOOK                     │
│                                                                   │
│  "List CSV files in my lakehouse"                               │
│           ↓                                                      │
│  FabricMLCredential.get_token()                                 │
│  (Gets token with ml.azure.com scope)                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ↓
        ┌─────────────────────────────────────┐
        │   AZURE AI FOUNDRY AGENT            │
        │   ┌─────────────────────────────┐   │
        │   │  Parse user message         │   │
        │   │  Determine which tool to    │   │
        │   │  call (listFiles, etc)      │   │
        │   └─────────────────────────────┘   │
        └─────────────────┬───────────────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
            ↓                            ↓
    ┌──────────────────┐       ┌──────────────────┐
    │ Call Tool 1:     │       │ Call Tool 2:     │
    │ listFiles        │       │ readCSVFile      │
    │ (HTTP POST)      │       │ (HTTP POST)      │
    └────────┬─────────┘       └────────┬─────────┘
             │                          │
             └──────────────┬───────────┘
                            │
                            ↓
        ┌─────────────────────────────────────────┐
        │     AZURE FUNCTIONS (Tool Endpoints)    │
        │                                          │
        │  @app.route("/listFiles")               │
        │  @app.route("/readCSVFile")             │
        │  @app.route("/getLakehouseInfo")        │
        │                                          │
        │  Each function:                         │
        │  1. Validates input                     │
        │  2. Creates credential                  │
        │  3. Calls lakehouse tool                │
        │  4. Returns JSON response               │
        └─────────────────┬──────────────────────┘
                          │
                          ↓
        ┌─────────────────────────────────────────┐
        │  LAKEHOUSE TOOLS (agent_lakehouse...)   │
        │                                          │
        │  FabricLakehouseCredential.get_token()  │
        │  (Gets token with powerbi/api scope)    │
        │                                          │
        │  Connect to OneLake (Fabric storage)    │
        │  - list_lakehouse_files()               │
        │  - read_csv_file()                      │
        │  - get_lakehouse_info()                 │
        └─────────────────┬──────────────────────┘
                          │
                          ↓
        ┌─────────────────────────────────────────┐
        │     FABRIC LAKEHOUSE (OneLake)          │
        │                                          │
        │  /workspace_id/lakehouse_id/Files/      │
        │  ├─ data.csv                            │
        │  ├─ report.csv                          │
        │  └─ ...                                 │
        └─────────────────┬──────────────────────┘
                          │
                          ↓ (Returns file list/content)
        ┌─────────────────────────────────────────┐
        │  Parse & Format Response                │
        │  Return JSON                            │
        └─────────────────┬──────────────────────┘
                          │
                          ↓
        ┌─────────────────────────────────────────┐
        │  Azure AI Foundry Agent                 │
        │  Process tool result                    │
        │  Generate response                      │
        └─────────────────┬──────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   FABRIC NOTEBOOK USER                           │
│                                                                   │
│  "Found 3 CSV files:"                                           │
│  1. data.csv (1.2 MB)                                           │
│  2. report.csv (2.4 MB)                                         │
│  3. summary.csv (0.8 MB)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 AUTHENTICATION FLOW

### Path 1: Fabric Notebook → AI Foundry
```
Fabric Notebook
└─ FabricMLCredential.get_token()
   └─ notebookutils.credentials.getToken("https://ml.azure.com")
      └─ Returns token for AI Foundry
```

### Path 2: Azure Functions → Fabric Lakehouse
```
Azure Functions
└─ FabricLakehouseCredential.get_token()
   └─ DefaultAzureCredential()
      └─ Managed Identity or Service Principal
         └─ Gets token for PowerBI API scope
            └─ Returns token for Fabric access
```

---

## 📁 THREE CODE FILES

### 1. `fabric_ai_foundry_client.py` (142 lines)
**Location**: Runs in Fabric Notebooks
**Purpose**: User-facing code - initiates conversation with AI agent

**Key Classes**:
- `FabricMLCredential`: Gets auth token from Fabric
- `connect_to_ai_foundry()`: Creates client connection
- `run_agent_conversation()`: Sends message and gets response

**Usage**:
```python
client, agent = connect_to_ai_foundry(ENDPOINT, AGENT_ID)
response = run_agent_conversation(client, agent, "List CSV files")
```

---

### 2. `agent_lakehouse_tools.py` (224 lines)
**Location**: Runs in Azure AI Foundry (as tools)
**Purpose**: Tool implementations that AI agent calls

**Key Classes**:
- `FabricLakehouseCredential`: Gets token with PowerBI scope

**Key Functions**:
- `list_lakehouse_files()`: List all files in lakehouse
  - Input: workspace_id, lakehouse_id, path, extension
  - Output: JSON list of files

- `read_csv_file()`: Read CSV file content
  - Input: workspace_id, lakehouse_id, file_path
  - Output: JSON with CSV data (first 100 rows)

- `get_lakehouse_info()`: Get metadata about lakehouse
  - Input: workspace_id, lakehouse_id
  - Output: JSON with info

**Mapping to OpenAPI**:
```
TOOL_FUNCTIONS = {
    "listFiles": list_lakehouse_files,
    "readCSVFile": read_csv_file,
    "getLakehouseInfo": get_lakehouse_info
}
```

---

### 3. `function_app.py` (216 lines)
**Location**: Deployed as Azure Function App
**Purpose**: HTTP endpoints that expose agent tools

**Key Endpoints**:

1. **POST /listFiles**
   - Validates input: workspace_id, lakehouse_id required
   - Calls: `list_lakehouse_files()`
   - Returns: JSON list of files

2. **POST /readCSVFile**
   - Validates input: workspace_id, lakehouse_id, file_path required
   - Calls: `read_csv_file()`
   - Returns: JSON with CSV content

3. **POST /getLakehouseInfo**
   - Validates input: workspace_id, lakehouse_id required
   - Calls: `get_lakehouse_info()`
   - Returns: JSON with metadata

4. **GET /health**
   - Simple health check endpoint
   - Returns: {"status": "healthy"}

---

## 🔄 CONVERSATION EXAMPLE

### User Types (in Fabric Notebook)
```
"List the CSV files in my lakehouse and tell me their sizes"
```

### Processing Steps

```
Step 1: Fabric Notebook
└─ Authenticate to AI Foundry
└─ Send message to agent

Step 2: AI Foundry Agent
└─ Parse: "List CSV files"
└─ Call tool: listFiles
   └─ POST to Azure Function

Step 3: Azure Functions
└─ Validate parameters
└─ Call list_lakehouse_files()

Step 4: Lakehouse Tools
└─ Authenticate to Fabric
└─ Query OneLake storage
└─ Filter .csv files
└─ Return: [
     {"name": "data.csv", "size": 1200000},
     {"name": "report.csv", "size": 2400000}
   ]

Step 5: AI Foundry Agent
└─ Receive tool response
└─ Format human response:
   "Found 2 CSV files:
    - data.csv (1.2 MB)
    - report.csv (2.4 MB)"

Step 6: Fabric Notebook
└─ Display response to user
```

---

## 🎯 KEY INTERACTIONS

### 1. Fabric Notebook ↔ AI Foundry
- **Protocol**: Azure AI Client SDK
- **Auth**: Fabric notebook credentials (ml.azure.com scope)
- **Flow**: Send message → Get response

### 2. AI Foundry ↔ Azure Functions
- **Protocol**: HTTP POST (OpenAPI defined)
- **Auth**: Function key or Azure AD
- **Flow**: Call tool endpoint → Get JSON

### 3. Azure Functions ↔ Fabric Lakehouse
- **Protocol**: Azure Storage SDK (OneLake)
- **Auth**: Managed Identity/Service Principal (powerbi/api scope)
- **Flow**: Query files → Download content

---

## 📦 OPENAPI SPECIFICATION

**File**: `openapi_spec.json`

**Purpose**: Defines tools available to AI agent

**Contains**:
```json
{
  "tools": [
    {
      "name": "listFiles",
      "description": "List files in lakehouse",
      "url": "https://functions.azurewebsites.net/listFiles",
      "parameters": [
        "workspace_id", "lakehouse_id", "path", "extension"
      ]
    },
    {
      "name": "readCSVFile",
      "description": "Read CSV file",
      "url": "https://functions.azurewebsites.net/readCSVFile",
      "parameters": [
        "workspace_id", "lakehouse_id", "file_path"
      ]
    }
  ]
}
```

---

## 📋 REQUIREMENTS

**Python Dependencies**:
```
azure-ai-projects>=1.0.0              # AI Foundry SDK
azure-identity>=1.15.0                # Authentication
azure-storage-file-datalake>=12.14.0  # Lakehouse access
pandas>=2.0.0                         # Data processing
```

**Azure Resources**:
1. Fabric Workspace + Lakehouse
2. AI Foundry Project + Agent
3. Azure Function App (with managed identity)
4. Appropriate permissions configured

---

## ✅ WHAT THIS ENABLES

- ✅ Users chat with AI agents in Fabric
- ✅ Agents can explore Fabric data
- ✅ Agents can read CSV files
- ✅ Agents can analyze and discuss data
- ✅ Real-time conversation with context
- ✅ Secure authentication between services

---

## 🚀 DEPLOYMENT ARCHITECTURE

```
User's Fabric Notebook
        ↓
Creates AIProjectClient
        ↓
        ↓─────→ AI Foundry Endpoint
                        ↓
                    Agent processes
                        ↓
                        ↓─────→ Azure Function URL
                                    ↓
                              HTTP Request
                                    ↓
                                    ↓─────→ OneLake/Fabric
                                            ↓
                                        File Access
```

---

## 💡 SIMPLE ANALOGY

Think of it like this:

```
USER (Fabric) asks ASSISTANT (AI Foundry)
            ↓
ASSISTANT needs to LOOK UP DATA
            ↓
ASSISTANT asks TOOLS (Azure Functions)
            ↓
TOOLS fetch from STORAGE (Lakehouse)
            ↓
TOOLS return DATA
            ↓
ASSISTANT formats ANSWER
            ↓
USER sees RESPONSE
```

The whole system is glue code to let an AI agent talk to your data!
