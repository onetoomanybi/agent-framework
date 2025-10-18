# QUICK START REFERENCE

## Overview

Everything runs in Fabric and AI Foundry. No external Azure infrastructure.

```
Fabric Notebook
    ├─ fabric_notebook_tools.py (tool implementations)
    └─ fabric_ai_foundry_client.py (agent connection)
           ↓
        AI Foundry Agent
           ↓
      (calls notebook functions)
```

## YOUR FIRST STEP (5 minutes)

```powershell
cd C:\repo\agent-framework\.workings
python validation_helpers.py
```

Expected: `15/15 checks passing ✓`

---

## THE 7-STEP DEPLOYMENT PATH

| Step | Where | What | Time |
|------|-------|------|------|
| 1 | Local | Validate code locally | 5 min |
| 2 | Local | Copy files to Willowbrook | 2 min |
| 3 | Fabric | Create notebook | 5 min |
| 4 | Fabric | Add tool code | 3 min |
| 5 | AI Foundry | Create agent | 5 min |
| 6 | AI Foundry | Register tools | 5 min |
| 7 | Fabric | Test agent | 5 min |

**Total: ~30 minutes**

---

## KEY COMMANDS

### Local validation

```powershell
cd C:\repo\agent-framework\.workings
python validation_helpers.py
```

### Copy files

```powershell
Copy-Item C:\repo\agent-framework\.workings\fabric_notebook_tools.py `
          C:\repo\agent-framework\willowbrook\src\
Copy-Item C:\repo\agent-framework\.workings\fabric_ai_foundry_client.py `
          C:\repo\agent-framework\willowbrook\src\
```

### In Fabric Notebook

```python
%pip install azure-ai-projects azure-identity
```

---

## FILES YOU NEED

| File | Where | Purpose |
|------|-------|---------|
| `fabric_notebook_tools.py` | Fabric notebook | Tool implementations |
| `fabric_ai_foundry_client.py` | Fabric notebook | Agent connection |
| `openapi_spec.json` | Reference only | Documents the API |

---

## WHAT GETS CREATED

In **Fabric Workspace**:
- New notebook: "WillowbrookAgent"
- Tool functions registered

In **AI Foundry**:
- New agent with notebook functions
- Tool definitions for listFiles, readCSVFile, getLakehouseInfo

Nothing created in Azure.

---

## SUCCESS INDICATORS

✓ Step 1: Validation shows 15/15 checks
✓ Step 3: Notebook created and runs
✓ Step 4: Tool code copied successfully
✓ Step 5: Agent created in AI Foundry
✓ Step 6: Agent recognizes notebook functions
✓ Step 7: Agent responds to queries using tools

---

## COMMON ISSUES

| Problem | Fix |
|---------|-----|
| Import errors | `pip install -r requirements.txt` |
| Notebook won't run | Attach compute to workspace |
| Tools not found in agent | Refresh agent tool registration |
| Authentication fails | Check Fabric credentials |

---

## DOCUMENTATION

- **Full guide**: `GETTING_STARTED.md`
- **Architecture**: `docs/OPENAPI_ARCHITECTURE.md`
- **Implementation**: `src/` folder files

---

**Status**: Ready to deploy ✓  
**Infrastructure needed**: None (Fabric + AI Foundry only)
