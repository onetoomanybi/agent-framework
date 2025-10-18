# Step-by-Step Deployment Guide with Testing Checkpoints

## Overview

This guide breaks deployment into 6 phases with a test at each phase. Each phase should be completed and verified before moving to the next.

---

## PHASE 1: Local Setup (5 minutes)

### What You're Doing
Copying remaining files to Willowbrook and validating all code locally.

### Step 1.1: Copy Remaining Files

Copy the client code and requirements:

```powershell
Copy-Item C:\repo\agent-framework\.workings\fabric_ai_foundry_client.py `
          C:\repo\agent-framework\willowbrook\src\

Copy-Item C:\repo\agent-framework\.workings\requirements.txt `
          C:\repo\agent-framework\willowbrook\
```

Verify files are in place:

```powershell
ls C:\repo\agent-framework\willowbrook\src\
ls C:\repo\agent-framework\willowbrook\requirements.txt
```

Expected output:
```
fabric_notebook_tools.py
fabric_ai_foundry_client.py
```

### Step 1.2: Run Local Validation

```powershell
cd C:\repo\agent-framework\.workings
python validation_helpers.py
```

### ✅ TEST CHECKPOINT 1: Local Validation

**Expected**: All 15 checks pass

```
✓ Phase 1: Code validation (3/3)
✓ Phase 2: Dependency analysis (4/4)
✓ Phase 3: Authentication flow (3/3)
✓ Phase 4: Integration patterns (3/3)
✓ Phase 5: Production readiness (2/2)

TOTAL: 15/15 checks passing ✓
Status: READY FOR DEPLOYMENT
```

**If this fails**: 
- Check dependencies: `pip install -r requirements.txt`
- Rerun validation

**If this passes**: ✅ Move to PHASE 2

---

## PHASE 2: Fabric Notebook Creation (10 minutes)

### What You're Doing
Creating a Fabric notebook and setting up the tool functions.

### Step 2.1: Create Notebook in Fabric

1. Go to your Fabric workspace (https://fabric.microsoft.com)
2. Click "+ New" → "Notebook"
3. Name it: `WillowbrookAgent`
4. Click "Create"

### Step 2.2: Copy Tool Functions to Notebook

1. Open `C:\repo\agent-framework\willowbrook\src\fabric_notebook_tools.py`
2. Copy the entire file contents
3. In your Fabric notebook, create a new cell (Cell 1)
4. Paste the code
5. Run the cell

Expected: Cell runs without errors (imports and functions are defined)

### Step 2.3: Install Dependencies

In Cell 2 of the notebook:

```python
%pip install azure-ai-projects azure-identity
```

Run the cell. Expected: Packages install successfully.

### Step 2.4: Verify Imports

In Cell 3:

```python
# Test that imports work
import json
import logging
import pandas as pd
from typing import Dict, Any, List, Optional

print("✓ All imports successful")
```

Run the cell.

### ✅ TEST CHECKPOINT 2: Notebook Setup

**Expected**: 
- Cell 1 runs without errors
- Cell 2 installs packages
- Cell 3 prints "✓ All imports successful"

**If this fails**:
- Check Fabric workspace has compute attached
- Verify Python version (should be 3.9+)

**If this passes**: ✅ Move to PHASE 3

---

## PHASE 3: Test Tool Functions (15 minutes)

### What You're Doing
Running each tool function individually to verify they work.

### Step 3.1: Test list_lakehouse_files()

In a new notebook cell:

```python
# Test listing files
try:
    result = list_lakehouse_files(
        lakehouse_path="/Workspace/Lakehouses/default",
        path="Files"
    )
    result_obj = json.loads(result)
    print(f"✓ list_lakehouse_files works")
    print(f"  File count: {result_obj.get('file_count', 0)}")
    print(f"  Success: {result_obj.get('success', False)}")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run the cell.

### Step 3.2: Test read_csv_file()

In a new notebook cell:

```python
# Test reading CSV
try:
    result = read_csv_file(
        lakehouse_path="/Workspace/Lakehouses/default",
        file_path="Files/sample.csv",
        max_rows=10
    )
    result_obj = json.loads(result)
    print(f"✓ read_csv_file works")
    print(f"  Row count: {result_obj.get('row_count', 0)}")
    print(f"  Success: {result_obj.get('success', False)}")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run the cell.

**Note**: If `sample.csv` doesn't exist, this may fail - that's OK. The important thing is the function runs without syntax errors.

### Step 3.3: Test get_lakehouse_info()

In a new notebook cell:

```python
# Test getting lakehouse info
try:
    result = get_lakehouse_info(
        lakehouse_path="/Workspace/Lakehouses/default"
    )
    result_obj = json.loads(result)
    print(f"✓ get_lakehouse_info works")
    print(f"  File count: {result_obj.get('file_count', 0)}")
    print(f"  Folder count: {result_obj.get('folder_count', 0)}")
    print(f"  Success: {result_obj.get('success', False)}")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run the cell.

### ✅ TEST CHECKPOINT 3: Tool Functions

**Expected**: All three tool tests run without syntax errors

```
✓ list_lakehouse_files works
✓ get_lakehouse_info works
✓ read_csv_file works
```

**If this fails**:
- Check function syntax in fabric_notebook_tools.py
- Check Fabric has access to lakehouse
- Verify notebookutils is available in Fabric

**If this passes**: ✅ Move to PHASE 4

---

## PHASE 4: Create AI Foundry Agent (10 minutes)

### What You're Doing
Creating an agent in Azure AI Foundry and registering the notebook functions.

### Step 4.1: Go to AI Foundry

Navigate to: https://ai.azure.com

### Step 4.2: Create New Agent

1. Click "Agents" (or "Build" → "Agents")
2. Click "New Agent"
3. Fill in:
   - **Name**: `WillbrookAnalyticsAgent`
   - **Description**: `Agent that analyzes Fabric lakehouse data`
4. In the system message box, paste:

```
You are a Fabric data analysis assistant. Your job is to help users analyze data in the Fabric lakehouse.

You have access to the following tools:
- list_lakehouse_files: Lists files in the lakehouse
- read_csv_file: Reads and returns CSV data
- get_lakehouse_info: Returns lakehouse metadata

When users ask about data, use these tools to help them.
```

5. Click "Create"

### Step 4.3: Register Notebook Functions as Tools

1. In the agent editor, look for "Tools" section
2. Click "Add Tool" → "Notebook Function"
3. In the dialog:
   - Select your Fabric workspace
   - Select your notebook: `WillowbrookAgent`
   - Select function: `list_lakehouse_files`
4. Click "Add"

Repeat for:
- `read_csv_file`
- `get_lakehouse_info`

### Step 4.4: Save Agent

Click "Save" or "Publish"

### ✅ TEST CHECKPOINT 4: Agent Created

**Expected**: 
- Agent appears in AI Foundry
- All 3 notebook functions are registered as tools
- Agent has system message

Verification:
1. Go to Agents list
2. See "WillbrookAnalyticsAgent"
3. Click on it → see 3 tools listed

**If this fails**:
- Check notebook functions are exported correctly
- Verify notebook is saved
- Check AI Foundry workspace has agent permissions

**If this passes**: ✅ Move to PHASE 5

---

## PHASE 5: Test Agent-Tool Integration (10 minutes)

### What You're Doing
Testing that the agent can call each tool.

### Step 5.1: Test Agent with list_lakehouse_files

1. In AI Foundry agent interface, click "Test" or open the chat
2. Ask: "List the files in the lakehouse"
3. Wait for response

**Expected**: Agent calls `list_lakehouse_files` and returns file list

### Step 5.2: Test Agent with get_lakehouse_info

Ask: "What's the size of the lakehouse?"

**Expected**: Agent calls `get_lakehouse_info` and returns metadata

### Step 5.3: Test Agent with read_csv_file

Ask: "Read the sales.csv file" (or whatever CSV exists in your lakehouse)

**Expected**: Agent calls `read_csv_file` and returns data

### ✅ TEST CHECKPOINT 5: Agent-Tool Integration

**Expected**: 
- Agent successfully calls all 3 tools
- Agent returns structured responses
- No errors in tool execution

**Verification checklist**:
- [ ] Agent call 1: list_lakehouse_files returns file list
- [ ] Agent call 2: get_lakehouse_info returns metadata
- [ ] Agent call 3: read_csv_file returns CSV data

**If this fails**:
- Check notebook is still running
- Check tool parameters match what agent sends
- Check error messages in AI Foundry logs

**If this passes**: ✅ Move to PHASE 6

---

## PHASE 6: End-to-End Test (5 minutes)

### What You're Doing
Testing the complete workflow with natural language queries.

### Step 6.1: Natural Language Query 1

Ask the agent: "How many CSV files are in the lakehouse?"

**Expected**: Agent uses tools to answer the question

### Step 6.2: Natural Language Query 2

Ask the agent: "What's the structure of the sales data?"

**Expected**: Agent reads CSV and describes columns

### Step 6.3: Natural Language Query 3

Ask the agent: "Show me a summary of the data"

**Expected**: Agent reads data and provides summary

### ✅ TEST CHECKPOINT 6: End-to-End

**Expected**: Agent successfully answers all questions using tools

**Verification checklist**:
- [ ] Query 1: Agent uses list/info tools
- [ ] Query 2: Agent reads CSV file
- [ ] Query 3: Agent interprets data
- [ ] No errors in any conversation

**If this fails**:
- Check notebook is still running
- Check AI Foundry logs for errors
- Verify tool functions match agent expectations

**If this passes**: ✅ ALL TESTS PASS - READY TO COMMIT

---

## Summary: Testing Matrix

| Phase | Test | Checkpoint | Status |
|-------|------|------------|--------|
| 1 | Local validation | 15/15 checks | ⏳ |
| 2 | Notebook setup | Cells run | ⏳ |
| 3 | Tool functions | All 3 functions work | ⏳ |
| 4 | Agent creation | 3 tools registered | ⏳ |
| 5 | Agent-tool calls | Tools execute | ⏳ |
| 6 | End-to-end | Natural language | ⏳ |

---

## Next Step After All Tests Pass

Once all checkpoints pass:

```powershell
cd C:\repo\agent-framework

# Stage everything
git add willowbrook/

# Commit with message
git commit -m "Add Willowbrook agent: Fabric-native tool implementation with step-by-step testing"

# Push to dev_build branch
git push origin dev_build
```

---

## Quick Reference: Test Commands

### Phase 1
```powershell
python validation_helpers.py
```

### Phase 2
```python
# Cell 1: Paste fabric_notebook_tools.py
# Cell 2: %pip install azure-ai-projects azure-identity
# Cell 3: print("✓ All imports successful")
```

### Phase 3
```python
# Test each function individually
list_lakehouse_files()
read_csv_file()
get_lakehouse_info()
```

### Phase 4
Go to AI Foundry and create agent with tools

### Phase 5 & 6
Chat with agent in AI Foundry

---

**Start with PHASE 1 now. Let me know when each checkpoint passes!** ✓
