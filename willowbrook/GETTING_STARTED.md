# Getting Started: Deployment Guide

## Overview

This project runs entirely within Microsoft Fabric and Azure AI Foundry. No external Azure infrastructure needed.

- **Compute**: Fabric Notebook
- **Storage**: Fabric Lakehouse
- **AI**: Azure AI Foundry Agent
- **Infrastructure**: Zero (everything in Fabric/AI Foundry)

## The First Step - Local Validation

This is where you start. No Azure knowledge needed.

### What to do:

Open PowerShell and run:

```powershell
cd C:\repo\agent-framework\.workings
python validation_helpers.py
```

### What to expect:

You should see all 15 checks pass:

```
✓ Phase 1: Code validation (3/3)
✓ Phase 2: Dependency analysis (4/4)
✓ Phase 3: Authentication flow (3/3)
✓ Phase 4: Integration patterns (3/3)
✓ Phase 5: Production readiness (2/2)

Status: READY FOR DEPLOYMENT
```

### If it fails:

Install dependencies:

```powershell
pip install -r requirements.txt
python validation_helpers.py
```

---

## Step 2: Copy Code to Willowbrook

Copy the validated code files:

```powershell
Copy-Item -Path C:\repo\agent-framework\.workings\fabric_notebook_tools.py `
          -Destination C:\repo\agent-framework\willowbrook\src\

Copy-Item -Path C:\repo\agent-framework\.workings\fabric_ai_foundry_client.py `
          -Destination C:\repo\agent-framework\willowbrook\src\

Copy-Item -Path C:\repo\agent-framework\.workings\requirements.txt `
          -Destination C:\repo\agent-framework\willowbrook\
```

Verify:

```powershell
ls C:\repo\agent-framework\willowbrook\src\
```

---

## Step 3: Set Up in Fabric Workspace

### 3.1 Create a new notebook in your Fabric workspace

1. Go to your Fabric workspace
2. Click "+ New" → "Notebook"
3. Name it "WillowbrookAgent"

### 3.2 Copy tool code into notebook

In the first cell, copy the contents of `fabric_notebook_tools.py`:

```python
# Copy entire contents of fabric_notebook_tools.py here
```

### 3.3 Install dependencies

In the second cell:

```python
%pip install azure-ai-projects azure-identity
```

---

## Step 4: Create Agent in AI Foundry

### 4.1 Go to Azure AI Foundry

Navigate to: https://ai.azure.com

### 4.2 Create a new agent

1. Click "Agents" → "New Agent"
2. Give it a name: "Willowbrook Agent"
3. Add system message:

```
You are a Fabric data analysis assistant. 
You can list files in the lakehouse and read CSV data.
When users ask about data, use your tools to access the lakehouse.
```

### 4.3 Register the tool

1. In the agent editor, click "Add Tool" → "Notebook Function"
2. Select your Fabric notebook (WillowbrookAgent)
3. Select the function: `list_lakehouse_files`
4. Repeat for:
   - `read_csv_file`
   - `get_lakehouse_info`

---

## Step 5: Test in Fabric Notebook

In your Fabric notebook, add a cell:

```python
from fabric_notebook_tools import list_lakehouse_files

# Test listing files
result = list_lakehouse_files(
    lakehouse_path="/Workspace/Lakehouses/default",
    path="Files"
)

print(result)
```

Run it and verify you see file listings.

---

## Step 6: Connect Agent to Notebook

In another cell, use the client code:

```python
from fabric_ai_foundry_client import connect_to_ai_foundry

# Connect to your agent
agent_id = "YOUR_AGENT_ID"  # Get from AI Foundry
endpoint = "https://your-project.services.ai.azure.com"

client = connect_to_ai_foundry(
    endpoint=endpoint,
    agent_id=agent_id
)

# Now your agent can call the notebook functions!
```

---

## Step 7: Use the Agent

Ask the agent questions:

```python
# The agent will use your tools to answer
response = client.process_message("What CSV files are in our lakehouse?")
print(response)
```

---

## Validation Checklist

- [ ] Step 1: `python validation_helpers.py` shows 15/15 ✓
- [ ] Step 2: Files copied to `willowbrook/src/`
- [ ] Step 3: Notebook created in Fabric workspace
- [ ] Step 4: Agent created in AI Foundry
- [ ] Step 5: Tool functions registered in agent
- [ ] Step 6: Client code connects successfully
- [ ] Step 7: Agent responds to queries

When all boxes are checked, you're ready to go!

---

## Troubleshooting

**Validation fails**: Run `pip install -r requirements.txt`

**Notebook won't run**: Check Fabric workspace has compute attached

**Agent can't find tools**: Verify tool registration in AI Foundry

**Authentication fails**: Check Fabric workspace credentials

---

Questions? Check the files in `willowbrook/docs/` for more details.
