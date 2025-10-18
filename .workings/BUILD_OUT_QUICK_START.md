# Build Out Project - Quick Start Guide

## What You'll Build

A **production-ready Fabric + Azure AI Foundry integration** with:
- ✅ Three fully integrated components (Fabric client, Agent tools, Azure Functions)
- ✅ Professional testing framework with 15+ tests
- ✅ Agent system instructions with built-in testing patterns
- ✅ Sample test notebooks demonstrating each feature
- ✅ Local testing harness (no Azure required)
- ✅ Complete deployment documentation

---

## The 5 Phases (8-13 hours total)

### 🔧 Phase 1: Fix Critical Issues (1-2 hrs)
**Make code production-ready**

1. Add conditional import for `notebookutils` (works in Fabric AND local testing)
2. Verify SDK method names with azure-ai-projects v1.0.0 docs
3. Replace naive CSV parsing with pandas
4. Add pagination to file listing endpoint

**Result**: Code runs without errors, handles real data

---

### 🧪 Phase 2: Add Testing Framework (2-3 hrs)
**Enable automated validation**

1. Create pytest configuration and fixtures
2. Write 4+ agent tool tests
3. Write 3+ Fabric client tests
4. Write 3+ Azure Function endpoint tests

**Result**: Test suite with mock Azure services, runs locally

---

### 🤖 Phase 3: Agent Testing Instructions (1-2 hrs)
**Enable agents to test themselves**

1. Write system prompt with clear testing instructions
2. Create 4 test pattern examples (connection, discovery, reading, analysis)
3. Create 4 sample test notebooks
4. Build local testing harness with simulated lakehouse

**Result**: Agents can validate functionality immediately after deployment

---

### ✨ Phase 4: Improve Code Quality (1-2 hrs)
**Professional polish**

1. Replace duck-typed token object with proper `@dataclass`
2. Add comprehensive logging to all functions
3. Add environment variable validation with clear errors
4. Remove unused dependencies

**Result**: Clean, maintainable, debuggable code

---

### 📚 Phase 5: Documentation & Deployment (1-2 hrs)
**Ready for production**

1. Create deployment guide (step-by-step Azure setup)
2. Create testing guide (how to validate)
3. Add architecture diagrams
4. Ensure all configuration examples work

**Result**: Anyone can deploy and test successfully

---

## Key Features You'll Add

### 1. Robust Authentication
```python
# Works in Fabric AND local testing
try:
    import notebookutils  # Fabric environment
except ImportError:
    # Local testing - mock credentials
    class MockNotebookUtils:
        class credentials:
            @staticmethod
            def getToken(scope: str):
                return "mock-token-for-testing"
    notebookutils = MockNotebookUtils()
```

### 2. Professional Token Handling
```python
from dataclasses import dataclass

@dataclass
class TokenInfo:
    token: str
    expires_on: int

# Clean, typed, documented
```

### 3. Robust CSV Parsing
```python
# Handles: quoted fields, escaping, special characters
df = pd.read_csv(io.BytesIO(content))
data = df.head(100).to_dict(orient='records')
```

### 4. Pagination for Scale
```python
# Returns max 100 files per page
# Includes continuation_token for next page
# Handles 10,000+ file lakehouses
```

### 5. Agent Testing Instructions
```
Agent knows 4 test patterns:
✓ Basic connection test
✓ File discovery test  
✓ Data reading test
✓ Data analysis test

Can run autonomously or from user request
```

### 6. Local Testing (No Azure Needed!)
```python
simulator = LocalLakehouseSimulator()
files = simulator.list_files()      # Works!
data = simulator.read_file("sales.csv")  # Works!
# Test locally, deploy to Azure confidently
```

---

## Success Checklist

By completion, you'll have:

- [ ] All issues from ISSUES_QUICK_FIX_GUIDE.md resolved
- [ ] Test suite with >15 tests, >90% pass rate
- [ ] Local testing harness demonstrating all tools
- [ ] 4 sample test notebooks with clear instructions
- [ ] Agent system prompt with testing patterns
- [ ] Comprehensive logging throughout
- [ ] Professional token/config handling
- [ ] Deployment guide with step-by-step instructions
- [ ] Testing guide explaining validation
- [ ] Zero hardcoded credentials anywhere
- [ ] All config via environment variables

---

## Quick Reference: What Each Phase Provides

| Phase | Adds | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Bug fixes, SDK verification | 1-2h | Code review |
| 2 | 15+ automated tests | 2-3h | Phase 1 |
| 3 | Agent testing, sample notebooks | 1-2h | Phase 1 |
| 4 | Code quality, logging | 1-2h | Phase 1-2 |
| 5 | Documentation, deployment | 1-2h | Phase 1-4 |

---

## The Big Picture

```
TODAY (Current State)
├── Code works locally
├── 1 critical issue (notebookutils)
├── 3 high issues (SDK, CSV, pagination)
└── No testing infrastructure

↓ After Phase 1

AFTER FIXES (1-2 hours)
├── Code runs without errors
├── All SDK methods verified
├── Handles real data correctly
├── Scales to large lakehouses
└── Still no testing

↓ After Phases 2-3

WITH TESTING (Next 3-4 hours)
├── 15+ automated tests
├── Local testing harness (no Azure needed!)
├── Agent self-testing capability
├── Sample test notebooks
└── High confidence deployments

↓ After Phases 4-5

PRODUCTION READY (8-13 hours total)
├── Professional code quality
├── Comprehensive logging
├── Complete documentation
├── Step-by-step deployment guide
├── Testing validation guide
└── Ready for real users!
```

---

## Starting Right Now

1. **Open**: `BUILD_OUT_PROMPT.md` (comprehensive guide)
2. **Read**: Phase 1 (1-2 hours of focused work)
3. **Do**: Task 1.1 through 1.4 (fix the issues)
4. **Test**: Run the existing code with fixes
5. **Repeat**: Phases 2-5 in order

Each phase builds on previous ones. Go in order!

---

## File Organization After Build-Out

```
.workings/
├── fabric_ai_foundry_client.py     # Fixed + logging
├── agent_lakehouse_tools.py         # Fixed + pagination
├── function_app.py                  # Tested endpoints
├── openapi_spec.json                # Unchanged
├── requirements.txt                 # Cleaned up
│
├── config.py                        # NEW: Config validation
├── BUILD_OUT_PROMPT.md              # This guide
│
├── tests/                           # NEW: Test suite
│   ├── conftest.py                  # Fixtures
│   ├── test_agent_tools.py          # Tool tests
│   ├── test_fabric_client.py        # Fabric tests
│   ├── test_function_app.py         # Endpoint tests
│   ├── local_test_harness.py        # No-Azure testing
│   └── test_data/                   # Sample data
│
├── samples/                         # NEW: Test notebooks
│   ├── 1_basic_connection_test.py
│   ├── 2_file_discovery_test.py
│   ├── 3_csv_read_test.py
│   └── 4_analysis_test.py
│
└── docs/                            # NEW: Documentation
    ├── DEPLOYMENT_GUIDE.md
    ├── TESTING_GUIDE.md
    └── ARCHITECTURE.md
```

---

## Common Questions

**Q: Do I need Azure to build this?**
A: No! Phases 1-2 work entirely locally. Phase 5 shows deployment to Azure.

**Q: How long will it really take?**
A: 8-13 hours if you follow all phases. You can do Phase 1-3 (5-7 hours) for a working system and come back to 4-5 later.

**Q: Can I do phases out of order?**
A: Not recommended. Phase 1 (fixes) is required first. After that, you can do 2-5 in any order, but 1→2→3 is best.

**Q: What if I just want the fixes?**
A: Do Phase 1 (1-2 hours). Your code will then work. Phases 2-5 are about testing and deployment.

**Q: Will my Fabric notebooks still work?**
A: Yes! All changes are backward compatible. Existing code keeps working, just better.

---

## Next Steps

1. ✅ You have: `BUILD_OUT_PROMPT.md` (detailed guide)
2. ✅ You have: `HOW_AGENTS_CONNECT_TO_LAKEHOUSE.md` (architecture)
3. ✅ You have: `WHAT_AGENTS_DO.txt` (capabilities)
4. ✅ You have: `ISSUES_QUICK_FIX_GUIDE.md` (specific fixes)
5. **Next**: Open `BUILD_OUT_PROMPT.md` → Follow Phase 1

Good luck building! 🚀
