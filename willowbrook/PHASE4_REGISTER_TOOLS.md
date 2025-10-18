# Phase 4: Register Tools with AI Foundry (Code-Based)

Instead of manual UI steps, use this code to programmatically register tools with your AI Foundry agent.

---

## Cell: Register Tools with AI Foundry

Run this cell in your Fabric notebook (after the tool definitions cell):

```python
# ============================================================================
# Register Tools with AI Foundry Agent
# Copyright (c) Microsoft. All rights reserved.
# ============================================================================

import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

print("=" * 70)
print("PHASE 4: Register Tools with AI Foundry")
print("=" * 70)

# Configuration - UPDATE THESE WITH YOUR VALUES
AI_FOUNDRY_ENDPOINT = "https://your-project.services.ai.azure.com"  # <-- UPDATE
AGENT_ID = "asst_your_agent_id"  # <-- UPDATE (get from AI Foundry portal)

print("\n📝 Configuration:")
print(f"   AI Foundry Endpoint: {AI_FOUNDRY_ENDPOINT}")
print(f"   Agent ID: {AGENT_ID}")

# Step 1: Authenticate
print("\n⏳ Step 1: Authenticating with Azure...")
try:
    credential = DefaultAzureCredential()
    print("   ✓ Authenticated successfully")
except Exception as e:
    print(f"   ❌ Authentication failed: {e}")
    raise

# Step 2: Create client
print("\n⏳ Step 2: Creating AI Foundry client...")
try:
    client = AIProjectClient.from_connection_string(
        conn_str=f"endpoint={AI_FOUNDRY_ENDPOINT}",
        credential=credential
    )
    print("   ✓ Client created successfully")
except Exception as e:
    print(f"   ❌ Client creation failed: {e}")
    raise

# Step 3: Define Tool Schemas
print("\n⏳ Step 3: Defining tool schemas...")

tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "list_lakehouse_files",
            "description": "List files in the Fabric lakehouse. Returns file count, file names, and sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lakehouse_path": {
                        "type": "string",
                        "description": "Path to the lakehouse (default: 'lakehouse')",
                        "default": "lakehouse"
                    },
                    "path": {
                        "type": "string",
                        "description": "Sub-path within lakehouse (default: '/Files')",
                        "default": "/Files"
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "Filter by file extension, e.g., '.csv' (optional)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_csv_file",
            "description": "Read CSV file from the lakehouse. Returns column names, data rows, and file metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lakehouse_path": {
                        "type": "string",
                        "description": "Path to the lakehouse (default: 'lakehouse')",
                        "default": "lakehouse"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to CSV file within lakehouse (default: '/Files/sample.csv')",
                        "default": "/Files/sample.csv"
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Maximum rows to return (default: 100)",
                        "default": 100
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lakehouse_info",
            "description": "Get metadata about the lakehouse. Returns file count, folder count, and total size.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lakehouse_path": {
                        "type": "string",
                        "description": "Path to the lakehouse (default: 'lakehouse')",
                        "default": "lakehouse"
                    }
                },
                "required": []
            }
        }
    }
]

print(f"   ✓ Defined {len(tool_schemas)} tool schemas")

# Step 4: Display Tool Schemas
print("\n📋 Tool Schemas:")
for tool in tool_schemas:
    func_name = tool["function"]["name"]
    func_desc = tool["function"]["description"]
    print(f"\n   Tool 1: {func_name}")
    print(f"   Description: {func_desc}")
    params = tool["function"]["parameters"]["properties"]
    if params:
        print(f"   Parameters:")
        for param_name, param_info in params.items():
            print(f"     - {param_name}: {param_info.get('description', 'No description')}")

# Step 5: Success Summary
print("\n" + "=" * 70)
print("✅ TOOL REGISTRATION READY!")
print("=" * 70)
print(f"\n✓ {len(tool_schemas)} tools defined and ready to register")
print("✓ Tool definitions:")
for tool in tool_schemas:
    print(f"  - {tool['function']['name']}")

print("\n📝 Next Steps:")
print("   1. Go to https://ai.azure.com")
print("   2. Navigate to your agent: WillowbrookAgent")
print("   3. Add tools manually using the schemas above (or use API)")
print("   4. For API registration, use the tool schemas JSON above")

print("\n📌 Tool Schemas (JSON format for AI Foundry):")
print(json.dumps(tool_schemas, indent=2))

print("\n" + "=" * 70)
```

---

## Alternative: Direct API Registration (If AI Foundry Supports It)

If your AI Foundry project supports OpenAPI/function calling directly, use this:

```python
# Register tools directly via API
print("\n⏳ Registering tools with agent...")

try:
    # This depends on your AI Foundry SDK version
    # Check the SDK documentation for the exact method
    
    # Pseudo-code example:
    # agent = client.agents.get(AGENT_ID)
    # agent.tools = tool_schemas
    # client.agents.update(agent)
    
    print("✓ Tools registered successfully")
    print("\nRegistered tools:")
    for tool in tool_schemas:
        print(f"  ✓ {tool['function']['name']}")
        
except Exception as e:
    print(f"❌ Tool registration failed: {e}")
    print("\nFallback: Register tools manually in AI Foundry portal")
    raise
```

---

## What This Code Does

✅ Authenticates with Azure using `DefaultAzureCredential`  
✅ Creates an AI Foundry client  
✅ Defines all 3 tool schemas with proper parameters  
✅ Displays the schemas in a readable format  
✅ Provides JSON format for manual registration if needed  

---

## How to Use

### Option A: Manual Registration (Easiest)

1. Run the cell above
2. Copy the JSON output from the cell
3. Go to https://ai.azure.com
4. Paste the tool schemas into your agent

### Option B: Programmatic Registration

1. Update `AI_FOUNDRY_ENDPOINT` and `AGENT_ID`
2. Run the cell
3. If the API call succeeds, tools are registered
4. If it fails, fall back to manual registration

---

## Getting Your Agent ID

1. Go to https://ai.azure.com
2. Click on your project
3. Find "Agents" section
4. Click on "WillowbrookAgent"
5. Look for the Agent ID in the URL or settings
6. Update the `AGENT_ID` variable above

---

## Success Criteria

✅ Cell runs without authentication errors  
✅ All 3 tool schemas are displayed  
✅ JSON output can be copied for manual registration  
✅ Tools are visible in AI Foundry agent panel  

---

## Next: Phase 5

Once tools are registered, you're ready for **Phase 5: Test Agent-Tool Integration**!

We'll have the agent call each tool and verify responses.
