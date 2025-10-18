# Quick Start: Adding Lakehouse Path

## TL;DR

The agent needs the **lakehouse path** to call the tool functions. Include it in your test queries.

## Lakehouse Path Format

```text
abfss://[workspace_name]@[tenant]/[lakehouse_name].Lakehouse/Files
```

### Real Example
```text
abfss://MyWorkspace@mycompany/MyLakehouse.Lakehouse/Files
```

## How to Find Your Lakehouse Path

1. Open **Microsoft Fabric**
2. Go to your **Lakehouse**
3. Click **⋮ (More options)** → **Properties**
4. Copy the **ABFSS Path**

## Three Ways to Test

### Option 1: Updated Test Script (Easiest)

```powershell
# 1. Edit phase5_test_with_lakehouse_path.py
#    Replace SAMPLE_LAKEHOUSE_PATH with your actual path

# 2. Run it
python willowbrook/src/phase5_test_with_lakehouse_path.py
```

### Option 2: AI Foundry Agent Playground

1. Go to https://ai.azure.com
2. Open your WillowbrookFabricAgent
3. In the test panel, ask:
   ```
   List files in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files
   ```

### Option 3: Python SDK (Custom Code)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint="https://marti-mgv56lom-francecentral.services.ai.azure.com/api/projects/marti-mgv56lom-francece-project",
    credential=DefaultAzureCredential()
)

# Create thread and run with lakehouse path in query
result = client.agents.create_thread_and_run(
    agent_id="asst_ipZYYYbuhCMCTSx5fai4b1md",
    messages=[{
        "role": "user",
        "content": "List files in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files"
    }]
)
```

## What Happens When You Add the Path

✅ Agent receives the lakehouse path
✅ Agent extracts the path parameter
✅ Agent calls the appropriate tool function
✅ Tool function runs in your Fabric notebook
✅ Results returned to agent
✅ Agent responds with the data

## Available Tool Functions

Once you add the lakehouse path, the agent can call:

1. **list_lakehouse_files(lakehouse_path, path, file_extension)**
   - Lists all files in your lakehouse
   - Returns: file names, sizes, modification times

2. **get_lakehouse_info(lakehouse_path)**
   - Gets metadata about the lakehouse
   - Returns: total file count, total size, folder count

3. **read_csv_file(lakehouse_path, file_path, max_rows)**
   - Reads a CSV file and returns data
   - Returns: file contents as JSON

## Example Queries

```text
# List files
"List all files in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files"

# Get metadata
"What's the total storage used in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files?"

# Read CSV
"Read the data from data.csv in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files"

# Complex queries
"How many CSV files are in my lakehouse at abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files?"
```

## Need Help?

- **Can't find your lakehouse path?** → See LAKEHOUSE_PATH_GUIDE.md
- **Agent still asking for path?** → Check that path is in the query
- **Tool not calling?** → Verify path format (abfss:// prefix required)
- **Connection error?** → Ensure Fabric workspace and lakehouse exist and are accessible
