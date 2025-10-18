# Phase 4: Agent Registration Complete ✅

Great news! You've successfully created your AI Foundry agent. Here are your details:

---

## 🎯 Agent Details

| Property | Value |
|----------|-------|
| **Agent Name** | WillowbrookAgent |
| **Agent ID** | `asst_KjZwGAAWsrAvXLsVbMBTqZZb` |
| **Project Endpoint** | `https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01` |
| **Project ID** | `proj-suk-dev-01` |

---

## ✅ Status: Phase 4 Complete

Your agent has been created in AI Foundry!

**What you need to do now:**

1. **Register the 3 tools** (If not already done via UI):
   - `list_lakehouse_files`
   - `read_csv_file`
   - `get_lakehouse_info`

   Reference: `PHASE4_MANUAL_TOOL_REGISTRATION.md` for tool code and schemas

2. **Verify tools are registered**:
   - Go to https://ai.azure.com
   - Open agent settings
   - Check "Tools" section has all 3 tools

---

## 🚀 Phase 5: Test Agent-Tool Integration

Run this to test if your agent can call the tools:

```bash
python willowbrook/src/phase5_test_agent_tools.py
```

This script will:
- ✓ Connect to your agent
- ✓ Send test queries
- ✓ Verify tool execution
- ✓ Display responses

**Test queries:**
- "List the files in my lakehouse"
- "What's the lakehouse metadata?"
- "Can you tell me about the files in my lakehouse?"

---

## 🧪 Phase 6: End-to-End Natural Language Test

Run this to test complex natural language queries:

```bash
python willowbrook/src/phase6_natural_language_test.py
```

This script will test:
- ✓ File discovery ("How many CSV files?")
- ✓ Data structure ("What's the data structure?")
- ✓ Storage analysis ("Tell me about storage usage")
- ✓ Complex queries (multiple tools)

---

## 📝 Client Code

Your agent client code (provided in attachment):

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01"
)

agent = project.agents.get_agent("asst_KjZwGAAWsrAvXLsVbMBTqZZb")

thread = project.agents.threads.create()
message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hello Agent"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id
)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(
        thread_id=thread.id,
        order=ListSortOrder.ASCENDING
    )
    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")
```

This is now saved as: `willowbrook/src/phase5_test_agent_tools.py`

---

## 🔧 Configuration

All scripts use:
- **Endpoint**: `https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01`
- **Agent ID**: `asst_KjZwGAAWsrAvXLsVbMBTqZZb`
- **Auth**: `DefaultAzureCredential()` (uses your logged-in Azure identity)

---

## ⚠️ Important: Tool Registration

**BEFORE running Phase 5 tests**, ensure your 3 tools are registered with the agent:

### Option 1: Manual Registration (UI)
1. Go to https://ai.azure.com
2. Open "WillowbrookAgent"
3. Click "Tools" or "Add Tool"
4. Register each tool:
   - Copy code from `PHASE4_MANUAL_TOOL_REGISTRATION.md`
   - Paste function code
   - Paste JSON schema
   - Save

### Option 2: Check Existing Tools
Run verification script:
```bash
python willowbrook/src/phase4_verify_agent.py
```

This will show:
- ✓ Agent connection status
- ✓ Number of registered tools
- ✓ Tool names
- ✓ Next steps

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `phase4_verify_agent.py` | Verify agent and tools |
| `phase5_test_agent_tools.py` | Test agent-tool integration |
| `phase6_natural_language_test.py` | End-to-end testing |
| `PHASE4_QUICK_START.md` | Quick reference |
| `PHASE4_MANUAL_TOOL_REGISTRATION.md` | Tool code and schemas |

All in: `c:\repo\agent-framework\willowbrook\src\`

---

## ✅ Next Steps

### Immediate:
1. Ensure 3 tools are registered in agent
2. Run Phase 5 test script
3. Verify agent calls tools correctly

### Then:
1. Run Phase 6 natural language tests
2. Verify complex queries work
3. Commit to dev_build

### Finally:
```bash
cd c:\repo\agent-framework
git add willowbrook/
git commit -m "Add Willowbrook agent with phase-by-phase deployment"
git push origin dev_build
```

---

## 🎉 Summary

**Phase 4: ✅ COMPLETE**
- Agent created in AI Foundry
- Agent ID: `asst_KjZwGAAWsrAvXLsVbMBTqZZb`
- Ready for tool registration

**Phase 5: ⏳ READY**
- Test scripts created
- Ready to execute: `python willowbrook/src/phase5_test_agent_tools.py`

**Phase 6: ⏳ READY**
- Natural language test script created
- Ready to execute: `python willowbrook/src/phase6_natural_language_test.py`

**Phase 7: ⏳ READY**
- Commit scripts ready
- Just run: `git add willowbrook/ && git commit && git push`

---

## 🆘 Troubleshooting

**Issue**: "Tools not found" in Phase 5 test
- **Fix**: Register tools via UI at https://ai.azure.com

**Issue**: "Agent not found"
- **Fix**: Check Agent ID is correct: `asst_KjZwGAAWsrAvXLsVbMBTqZZb`

**Issue**: "Authentication failed"
- **Fix**: Run `az login` and ensure you're authenticated to Azure

**Issue**: Script won't run
- **Fix**: Ensure requirements.txt packages installed: `pip install -r requirements.txt`
