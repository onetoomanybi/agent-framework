# Phase 4: Tool Registration - Complete Guide

## 📋 What You Need to Do

Register your 3 Fabric notebook tools with AI Foundry so the agent can call them.

---

## 🚀 Quickest Path (5 minutes)

### Step 1: View Tool Schemas
Open: `willowbrook/PHASE4_MANUAL_TOOL_REGISTRATION.md`

This file contains:
- Tool 1: `list_lakehouse_files` 
- Tool 2: `read_csv_file`
- Tool 3: `get_lakehouse_info`

Each with **Function Code** and **Parameter Schema** (JSON)

### Step 2: Go to AI Foundry
Navigate to: https://ai.azure.com

### Step 3: Register Tools
For each tool (copy code + schema from markdown):
1. Click **Add Tool**
2. Select **Python Function**
3. Paste code
4. Paste JSON schema
5. Click **Save**

### Step 4: Done!
All 3 tools should now appear in your agent's Tools panel.

---

## 📁 Reference Files

| File | Purpose |
|------|---------|
| `PHASE4_EXECUTION.md` | Step-by-step manual registration guide |
| `PHASE4_MANUAL_TOOL_REGISTRATION.md` | **Use this!** Complete tool code + schemas |
| `PHASE4_REGISTER_TOOLS.md` | Programmatic approach (advanced) |

---

## ✅ Success Checklist

After registering, verify:

```
[ ] Agent "WillowbrookAgent" exists
[ ] Tool 1: list_lakehouse_files is registered
[ ] Tool 2: read_csv_file is registered  
[ ] Tool 3: get_lakehouse_info is registered
[ ] All tools show in Tools panel
[ ] Each tool has correct parameters
```

---

## 🆘 If Something Goes Wrong

**Issue**: Tools not appearing
- **Fix**: Refresh page, check you're in correct project

**Issue**: JSON validation error
- **Fix**: Copy from markdown carefully (check for missing commas/braces)

**Issue**: "Function not found"
- **Fix**: Verify functions are defined in Fabric notebook Cell 1

---

## 📍 Current Progress

- ✅ Phase 1: Local setup (15/15 checks passing)
- ✅ Phase 2: Fabric notebook (functions defined)
- ✅ Phase 3: Tool testing (all functions working)
- 🟡 **Phase 4: Tool registration (YOU ARE HERE)**
- ⏳ Phase 5: Agent-tool integration
- ⏳ Phase 6: End-to-end testing

---

## 🎯 Next After Phase 4

Once tools are registered, you'll do **Phase 5**:
- Open agent chat
- Ask: "List files in my lakehouse"
- Agent calls `list_lakehouse_files`
- Verify response

---

## 📌 Key Files Location

All files in: `c:\repo\agent-framework\willowbrook\`

```
willowbrook/
├── PHASE4_MANUAL_TOOL_REGISTRATION.md ← COPY SCHEMAS FROM HERE
├── PHASE4_EXECUTION.md
├── PHASE4_REGISTER_TOOLS.md
├── PHASE2_NOTEBOOK_SETUP.md (tool definitions)
├── PHASE3_TEST_CELLS.md (test code)
└── src/
    ├── fabric_notebook_tools.py
    ├── fabric_ai_foundry_client.py
    └── requirements.txt
```

---

## 💡 Pro Tips

1. **Copy One Tool at a Time**: Don't try to register all 3 at once
2. **Test After Each**: After registering each tool, refresh and verify it appears
3. **Keep This Open**: Have `PHASE4_MANUAL_TOOL_REGISTRATION.md` in one window, AI Foundry in another
4. **Validate JSON**: If tool won't save, check JSON syntax using https://jsonlint.com

---

## ❓ Questions?

- **"What's a tool schema?"** → JSON definition of what parameters the function accepts
- **"Why 3 tools?"** → Each does a different task: list files, read data, get metadata
- **"Can I modify the tools?"** → Yes, but they're optimized for this use case
- **"What if registration fails?"** → Check error message, usually syntax issue in JSON

---

**Ready?** 👉 Open `PHASE4_MANUAL_TOOL_REGISTRATION.md` and start registering!
