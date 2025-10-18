# Phase 4: Register Tools - Execution Guide

## Overview

You have 3 tools to register with your AI Foundry agent. Two approaches:

1. **Simplest**: Copy JSON schemas from `PHASE4_MANUAL_TOOL_REGISTRATION.md` → Paste into AI Foundry UI
2. **Programmatic**: Run Python code that displays schemas

---

## Approach 1: Manual Registration (Recommended)

### Step 1: Get Tool Schemas

Open: `PHASE4_MANUAL_TOOL_REGISTRATION.md`

You'll find 3 sections:
- **Tool 1**: list_lakehouse_files (Function Code + Parameter Schema)
- **Tool 2**: read_csv_file (Function Code + Parameter Schema)
- **Tool 3**: get_lakehouse_info (Function Code + Parameter Schema)

### Step 2: Go to AI Foundry

1. Navigate to: https://ai.azure.com
2. Select your **project**
3. Go to **Agents** → **WillowbrookAgent**
4. Find **Tools** section

### Step 3: Add Tool 1 - list_lakehouse_files

1. Click **Add Tool** or **+ Add**
2. Select **Python Function** or **Custom Function**
3. Copy **Function Code** from the markdown file
4. Paste into code field
5. Copy **Parameter Schema** JSON
6. Paste into parameters field
7. Click **Save** or **Register**

### Step 4: Add Tool 2 - read_csv_file

Repeat Step 3 for the second tool

### Step 5: Add Tool 3 - get_lakehouse_info

Repeat Step 3 for the third tool

### Step 6: Verify

Check that all 3 tools appear in your agent's Tools panel:
- ✓ list_lakehouse_files
- ✓ read_csv_file
- ✓ get_lakehouse_info

---

## Approach 2: Programmatic Registration

Run this in your **Fabric Notebook** (in a new cell below your tool definitions):

```python
# Phase 4: Display Tool Schemas for Registration
print("=" * 70)
print("PHASE 4: Tool Registration Schemas")
print("=" * 70)

import json

tools = [
    {
        "name": "list_lakehouse_files",
        "description": "List files in the Fabric lakehouse",
        "parameters": {
            "type": "object",
            "properties": {
                "lakehouse_path": {
                    "type": "string",
                    "description": "Path to lakehouse",
                    "default": "lakehouse"
                },
                "path": {
                    "type": "string",
                    "description": "Sub-path within lakehouse",
                    "default": "/Files"
                },
                "file_extension": {
                    "type": "string",
                    "description": "Filter by extension (e.g. '.csv')"
                }
            }
        }
    },
    {
        "name": "read_csv_file",
        "description": "Read CSV file from the lakehouse",
        "parameters": {
            "type": "object",
            "properties": {
                "lakehouse_path": {
                    "type": "string",
                    "description": "Path to lakehouse",
                    "default": "lakehouse"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to CSV file",
                    "default": "/Files/sample.csv"
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Max rows to return",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "get_lakehouse_info",
        "description": "Get lakehouse metadata",
        "parameters": {
            "type": "object",
            "properties": {
                "lakehouse_path": {
                    "type": "string",
                    "description": "Path to lakehouse",
                    "default": "lakehouse"
                }
            }
        }
    }
]

print("\n✓ Defined 3 tool schemas\n")
for i, tool in enumerate(tools, 1):
    print(f"Tool {i}: {tool['name']}")
    print(f"  Description: {tool['description']}")
    print(f"  Parameters: {list(tool['parameters']['properties'].keys())}")
    print()

print("=" * 70)
print("JSON for AI Foundry:")
print("=" * 70)
print(json.dumps(tools, indent=2))

print("\n" + "=" * 70)
print("✅ Copy the JSON above and paste into AI Foundry Tools section")
print("=" * 70)
```

---

## Success Criteria

After completing this phase, verify:

- [ ] Agent "WillowbrookAgent" exists in AI Foundry
- [ ] All 3 tools are registered and visible
- [ ] Each tool shows correct description
- [ ] Each tool shows correct parameters
- [ ] No errors in tool definitions
- [ ] Tools are in "Active" or "Enabled" state

---

## If Tools Are Not Appearing

Try these troubleshooting steps:

1. **Refresh the page**: Sometimes changes take a moment to appear
2. **Check project**: Are you in the right AI Foundry project?
3. **Check agent**: Is it "WillowbrookAgent"?
4. **Verify syntax**: Is the JSON valid? (Use https://jsonlint.com/)
5. **Check permissions**: Do you have write access to the agent?

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Function not found" | Verify function exists in Fabric notebook Cell 1 |
| "Invalid parameter schema" | Check JSON syntax - missing braces or commas |
| "Agent doesn't exist" | Create agent first, then add tools |
| "Cannot save tool" | Try refreshing page and trying again |

---

## Next Phase

Once all 3 tools are registered: **Phase 5 - Test Agent-Tool Integration**

See `PHASE5_TEST_INTEGRATION.md` for:
- How to test each tool via agent chat
- Expected responses
- Troubleshooting if tools don't execute

---

## Reference Files

- `PHASE4_MANUAL_TOOL_REGISTRATION.md` - Complete tool code and schemas
- `PHASE4_REGISTER_TOOLS.md` - Programmatic registration approach
- `PHASE2_NOTEBOOK_SETUP.md` - Tool functions (Cell 1)
