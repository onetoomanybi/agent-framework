# Quick Reference: Ready to Test

## Your Agent is Ready ✅

**Agent ID:** `asst_KjZwGAAWsrAvXLsVbMBTqZZb`
**Endpoint:** `https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01`
**Status:** Active and configured

---

## Run Phase 5 Test Now

```powershell
cd c:\repo\agent-framework
python willowbrook/src/phase5_test_agent_tools.py
```

**This will:**
- Connect to your agent
- Send 3 test queries
- Display responses
- Verify tools work

**Expected output:**
```
TEST 1: List the files in my lakehouse
ASSISTANT: [Response with file list]

TEST 2: What's the lakehouse metadata?
ASSISTANT: [Response with size/count info]

TEST 3: Can you tell me about the files in my lakehouse?
ASSISTANT: [Response with file details]
```

---

## Then Run Phase 6 Test

```powershell
python willowbrook/src/phase6_natural_language_test.py
```

**This will:**
- Test complex natural language queries
- Verify agent uses tools appropriately
- Display responses

---

## Finally Commit

```powershell
cd c:\repo\agent-framework
git add willowbrook/
git commit -m "Add Willowbrook agent: Fabric-native implementation"
git push origin dev_build
```

---

## All Files Updated ✅

- ✅ phase4_verify_agent.py
- ✅ phase5_test_agent_tools.py
- ✅ phase6_natural_language_test.py
- ✅ Documentation complete

**All use your agent ID and endpoint.**

---

## Summary

| Phase | Status | Command |
|-------|--------|---------|
| 1-4 | ✅ Done | N/A |
| 5 | 🟡 Ready | `python willowbrook/src/phase5_test_agent_tools.py` |
| 6 | 🟡 Ready | `python willowbrook/src/phase6_natural_language_test.py` |
| 7 | 🟡 Ready | `git add && git commit && git push` |

**Next:** Run Phase 5 test! 🚀
