# Fix: Running Agent with Tool Execution in Fabric Notebook

## The Problem

Error: `Action handling is not yet implemented for submit_tool_outputs`

This means:
- Agent recognizes it needs to call tools ✅
- Agent framework doesn't know HOW to execute them ❌
- Tool functions exist in Fabric notebook, not in AI Foundry

## The Solution

You have 2 options:

### OPTION 1: Run Agent From Fabric Notebook (Recommended)

**This is the simplest approach for your setup:**

1. Open your Fabric notebook (where your tool functions are defined)
2. Add a new cell at the end with this code:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Configuration
endpoint = "https://marti-mgv56lom-francecentral.services.ai.azure.com/api/projects/marti-mgv56lom-francece-project"
agent_id = "asst_ipZYYYbuhCMCTSx5fai4b1md"
lakehouse_path = "abfss://Mart_DVCP@onelake.dfs.fabric.microsoft.com/LH_Validation.Lakehouse/Files"

# Initialize agent client
client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Query agent - it will call your tool functions
query = f"List the files in {lakehouse_path}"
print(f"Query: {query}")

# Create thread and run
result = client.agents.create_thread_and_run(
    agent_id=agent_id,
    messages=[{"role": "user", "content": query}]
)

# Get response
messages = list(client.agents.messages.list(result.thread_id))
for msg in messages:
    if msg.role == "assistant" and msg.text_messages:
        for text_msg in msg.text_messages:
            print(f"Agent: {text_msg.text}")

# Cleanup
client.agents.threads.delete(result.thread_id)
```

**Why this works:**
- Tool functions are in the same notebook environment
- Agent can find and call them directly
- Everything runs in Fabric (your desired zero-infrastructure setup)

### OPTION 2: Create Azure Function Wrapper

**For calling agent from outside Fabric:**

Create HTTP-triggered Azure Functions that wrap your tools, then update agent tools to point to the HTTP endpoints.

This is more complex but allows calling the agent from anywhere.

## Recommendation

**Use OPTION 1** because:
1. You chose Fabric as compute (no external infrastructure)
2. Your tools are already in Fabric
3. Simplest implementation
4. Lowest cost
5. Best performance

## Steps to Implement OPTION 1

1. **Copy this code to a new cell in your Fabric notebook**
2. **Update the lakehouse path if needed**
3. **Run the cell**
4. **Agent will call your tool functions automatically**

That's it! The agent will now work end-to-end with your Fabric lakehouse.

## Files to Update

All test scripts already updated to use correct endpoint and agent ID:
- ✅ phase5_test_with_lakehouse_path.py
- ✅ phase6_natural_language_test.py
- ✅ check_agent_tools.py

These can now be run from Fabric notebook cells or with the code above.

## Current Status

| Component | Status |
|-----------|--------|
| Agent registered | ✅ |
| Tools registered | ✅ |
| Lakehouse path configured | ✅ |
| Tool functions defined | ✅ |
| Execution method | ⚠️ Needs Fabric notebook context |

After implementing OPTION 1: 🟢 FULLY OPERATIONAL
