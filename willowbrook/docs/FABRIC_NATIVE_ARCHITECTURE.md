# Architecture: Fabric-Native Agent Tools

## Simplified Architecture (ZERO Azure Infrastructure)

```
┌─────────────────────────────────────────────┐
│         Fabric Workspace                    │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Notebook: WillowbrookAgent          │  │
│  │                                      │  │
│  │  fabric_notebook_tools.py            │  │
│  │  ├─ list_lakehouse_files()           │  │
│  │  ├─ read_csv_file()                  │  │
│  │  └─ get_lakehouse_info()             │  │
│  │                                      │  │
│  │  fabric_ai_foundry_client.py         │  │
│  │  ├─ connect_to_ai_foundry()          │  │
│  │  └─ process_messages()               │  │
│  └────────────┬─────────────────────────┘  │
│               │                             │
│               │ Registered as tool         │
│               │                             │
└───────────────┼─────────────────────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │  Azure AI Foundry Agent  │
    │                          │
    │  Agent calls notebook    │
    │  functions directly      │
    │  (no external endpoints) │
    │                          │
    └──────────────────────────┘
                │
                ▼
    ┌──────────────────────────┐
    │  Fabric Lakehouse        │
    │  (OneLake Storage)       │
    │  ├─ CSV Files            │
    │  ├─ Data                 │
    │  └─ Metadata             │
    └──────────────────────────┘
```

## Key Differences from Traditional Setup

| Aspect | Traditional | Fabric-Native |
|--------|-------------|---------------|
| Compute | Azure Functions | Fabric Notebook |
| Storage | Azure Storage | Fabric Lakehouse (OneLake) |
| Tool Hosting | External HTTP endpoints | Notebook functions |
| Infrastructure | Resource Groups, Storage Accounts, Function Apps | None |
| Authentication | Managed Identity, Service Principals | Fabric workspace credentials |
| Cost | Compute + Storage | Fabric Capacity only |

## How It Works

### 1. User Creates Fabric Notebook

```python
# In Fabric workspace, create a new notebook
# Name: WillowbrookAgent
```

### 2. Copy Tool Functions

```python
# Cell 1: Tool implementations
# Copy entire fabric_notebook_tools.py
```

### 3. Install Dependencies

```python
# Cell 2: Dependencies
%pip install azure-ai-projects azure-identity
```

### 4. Register with AI Foundry

```
AI Foundry Agent → Tools → Add Tool → Notebook Function
```

Select:
- Notebook: WillowbrookAgent
- Functions: list_lakehouse_files, read_csv_file, get_lakehouse_info

### 5. Agent Calls Tools Directly

When user asks: "What files are in the lakehouse?"

```
AI Foundry Agent
    ↓ (calls)
list_lakehouse_files()  ← Direct function call
    ↓ (accesses)
Fabric Lakehouse
    ↓ (returns)
JSON response
    ↓ (processes)
Agent responds to user
```

## No External Infrastructure Needed

❌ **NOT CREATED**:
- Resource Groups
- Storage Accounts
- Azure Function Apps
- Virtual Networks
- Service Principal roles in Azure AD

✅ **CREATED IN FABRIC**:
- Notebook
- Tool functions

✅ **CREATED IN AI FOUNDRY**:
- Agent
- Tool registrations

## Security Model

### Authentication

Fabric notebook authenticates using:
- Fabric workspace credentials (implicit)
- No external tokens needed
- No Managed Identity configuration

### Authorization

Access to lakehouse is controlled by:
- Fabric workspace permissions
- User role in workspace (Viewer, Editor, Admin)
- Lakehouse access control

## Cost Model

- **No additional compute charges** - Uses Fabric capacity
- **No storage charges** - Uses existing Fabric Lakehouse
- **No function app charges** - Everything in Fabric

Only cost: Your existing Fabric subscription.

## Advantages

✅ **Simpler**: No Azure infrastructure to manage
✅ **Faster**: Direct function calls, no HTTP latency
✅ **Cheaper**: No separate Function App costs
✅ **Integrated**: Runs natively in Fabric
✅ **Secure**: No external endpoints to expose

## Limitations

⚠️ **Notebook must be running** - Tools only available when notebook is active
⚠️ **Tied to workspace** - Can't call across workspaces easily
⚠️ **Notebook compute required** - Needs attach compute to workspace

## Deployment Steps

1. **Create Notebook** in Fabric workspace
2. **Copy tool code** into notebook
3. **Install dependencies** in notebook
4. **Register tools** in AI Foundry agent
5. **Test** in Fabric notebook

Total time: ~30 minutes
No Azure CLI commands needed.

---

**Status**: Simplified, integrated, zero-infrastructure ✓
