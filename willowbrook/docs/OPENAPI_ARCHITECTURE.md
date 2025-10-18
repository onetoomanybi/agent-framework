# Architecture: OpenAPI Agent Tools

## Current Architecture (CORRECT ✓)

```
┌─────────────────────────────────────────────────────────────────┐
│                   Azure AI Foundry Agent                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Agent                                                   │  │
│  │ • Processes natural language from user                 │  │
│  │ • Makes OpenAPI 3 calls to registered tools            │  │
│  │ • Interprets tool responses                            │  │
│  └────────┬──────────────────────────────────────────────┬┘  │
│           │                                              │     │
│           │ Calls via OpenAPI 3                         │     │
│           │ (HTTP POST requests)                        │     │
│           │                                              │     │
└───────────┼──────────────────────────────────────────────┼─────┘
            │                                              │
            ▼                                              ▼
    ┌──────────────────┐                        ┌──────────────────┐
    │ Endpoint 1       │                        │ Endpoint 2       │
    │ /listFiles       │                        │ /readCSVFile     │
    │ (HTTP POST)      │                        │ (HTTP POST)      │
    └────────┬─────────┘                        └────────┬─────────┘
             │                                           │
             ▼                                           ▼
    ┌──────────────────────────────────────────────────────────────┐
    │             Azure Functions or Fabric Job                   │
    │                                                              │
    │  agent_lakehouse_tools.py                                   │
    │  ├─ list_lakehouse_files()                                  │
    │  ├─ read_csv_file()                                         │
    │  └─ get_lakehouse_info()                                    │
    │                                                              │
    │  ↓ (Authenticates via Managed Identity)                     │
    │                                                              │
    └────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Microsoft Fabric          │
            │  Lakehouse (OneLake)       │
            │  ├─ CSV Files              │
            │  ├─ Data                   │
            │  └─ Metadata               │
            └────────────────────────────┘
```

## How It Works

### 1. Agent Makes OpenAPI Call

Agent decides to list files:

```
POST https://your-function-app.azurewebsites.net/api/listFiles
Content-Type: application/json

{
  "workspace_id": "12345678-1234-1234-1234-123456789012",
  "lakehouse_id": "87654321-4321-4321-4321-210987654321",
  "path": "Files",
  "file_extension": ".csv"
}
```

### 2. Endpoint Receives Request

The HTTP endpoint (hosted in Azure Functions) receives the request.

### 3. Tool Logic Executes

The `agent_lakehouse_tools.py` functions execute:
- Authenticate to Fabric
- Read files from OneLake
- Process the response

### 4. Response Returned as JSON

```json
{
  "success": true,
  "file_count": 3,
  "files": [
    {"name": "sales.csv", "size": 1024, "last_modified": "2025-10-18T10:00:00Z"},
    {"name": "data.csv", "size": 2048, "last_modified": "2025-10-18T10:30:00Z"}
  ]
}
```

### 5. Agent Processes Response

Agent receives the JSON and continues the conversation with the user.

---

## What's Defined Where

| Component | Location | Purpose |
|-----------|----------|---------|
| **OpenAPI Spec** | `openapi_spec.json` | Defines the 3 endpoints for the agent |
| **Tool Functions** | `agent_lakehouse_tools.py` | Implements listFiles, readCSVFile, getLakehouseInfo |
| **HTTP Endpoints** | `function_app.py` | Wraps tool functions as Azure Function HTTP triggers |
| **Client Code** | `fabric_ai_foundry_client.py` | Runs in Fabric notebook, calls the agent |

---

## Registration Steps

### In Azure AI Foundry Portal:

1. **Upload OpenAPI Spec**
   - `openapi_spec.json` defines the 3 operations

2. **Configure Server URL**
   - Points to where endpoints are hosted
   - `https://your-function-app.azurewebsites.net/api`

3. **Agent Automatically Calls Them**
   - When agent needs to list files → calls `/listFiles`
   - When agent needs to read CSV → calls `/readCSVFile`
   - When agent needs metadata → calls `/getLakehouseInfo`

---

## Current Status ✓

✅ OpenAPI 3.1.0 compliant
✅ 3 well-defined operations
✅ Proper request/response schemas
✅ Security configuration (OAuth2/Azure AD)
✅ Retry logic with exponential backoff
✅ Comprehensive logging
✅ Production-ready

---

**This architecture is already correct for OpenAPI agent tools.**

The agent calls your endpoints via HTTP POST with JSON payloads, receives JSON responses, and continues processing.

No changes needed - the code is already set up this way! ✓
