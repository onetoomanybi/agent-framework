# Willowbrook Documentation Index

## Quick Navigation

### 🚀 Just Want to Deploy?
**Start here**: `GETTING_STARTED.md` (7 simple steps, ~30 min)

### ⚡ Need Quick Reference?
**Go here**: `QUICK_START.md` (Commands and checklist)

### 🏗️ Want to Understand the Architecture?
**Read this**: `docs/FABRIC_NATIVE_ARCHITECTURE.md` (How it all works)

### 📝 What Changed from the Original Plan?
**See here**: `ARCHITECTURE_CHANGES.md` (Old vs. new approach)

### 📖 Need Full Details?
**Check**: `DEPLOYMENT_GUIDE.md` (Comprehensive reference)

---

## Documentation Map

```
willowbrook/
│
├── 🟢 START HERE
│   ├─ GETTING_STARTED.md          [7-step deployment guide]
│   └─ QUICK_START.md              [Quick reference & commands]
│
├── 📋 UNDERSTAND
│   ├─ DEPLOYMENT_SUMMARY.md       [What changed & why]
│   ├─ ARCHITECTURE_CHANGES.md     [Before/after comparison]
│   └─ DEPLOYMENT_GUIDE.md         [Full reference]
│
├── 🏗️ ARCHITECTURE
│   └─ docs/
│       ├─ FABRIC_NATIVE_ARCHITECTURE.md   [New: Fabric-native design]
│       └─ OPENAPI_ARCHITECTURE.md         [How agent tools work]
│
├── 💾 SOURCE CODE
│   └─ src/
│       ├─ fabric_notebook_tools.py        [Tool implementations]
│       └─ fabric_ai_foundry_client.py     [Client code]
│
├── 📦 DEPENDENCIES
│   ├─ requirements.txt             [Python packages]
│   └─ spec/openapi_spec.json       [API specification]
│
└── 🧪 TEST & VALIDATE
    └─ Copy from .workings/
       ├─ validation_helpers.py      [Run: python validation_helpers.py]
       └─ requirements.txt           [Already in root]
```

---

## Workflow

### Phase 1: Preparation (5 min)
1. Read: `QUICK_START.md`
2. Run: `python validation_helpers.py`

### Phase 2: Setup (10 min)
1. Read: `GETTING_STARTED.md` Steps 1-2
2. Copy files to `src/` folder

### Phase 3: Deploy (15 min)
1. Read: `GETTING_STARTED.md` Steps 3-7
2. Follow step-by-step in Fabric & AI Foundry

### Phase 4: Validate (5 min)
1. Check `QUICK_START.md` validation checklist
2. Test agent in Fabric notebook

---

## Key Files by Role

### For Developers
- `src/fabric_notebook_tools.py` - Core tool functions
- `src/fabric_ai_foundry_client.py` - Integration code
- `spec/openapi_spec.json` - API definition

### For Operators/Deployers
- `GETTING_STARTED.md` - Deployment steps
- `QUICK_START.md` - Commands and troubleshooting
- `docs/FABRIC_NATIVE_ARCHITECTURE.md` - How it works

### For Architects/Decision Makers
- `ARCHITECTURE_CHANGES.md` - Why we changed
- `DEPLOYMENT_SUMMARY.md` - Benefits overview
- `docs/FABRIC_NATIVE_ARCHITECTURE.md` - Technical design

---

## Common Questions

**Q: Where do I start?**  
A: `GETTING_STARTED.md` - Follow the 7 steps.

**Q: What if I get an error?**  
A: Check `QUICK_START.md` troubleshooting section.

**Q: Why no Azure infrastructure?**  
A: See `ARCHITECTURE_CHANGES.md` for benefits.

**Q: How does the agent call the tools?**  
A: See `docs/FABRIC_NATIVE_ARCHITECTURE.md`.

**Q: What exactly changed?**  
A: See `DEPLOYMENT_SUMMARY.md`.

**Q: Do I need to install anything special?**  
A: Just `pip install -r requirements.txt` locally for validation.

---

## Document Details

| Document | Size | Read Time | Purpose |
|----------|------|-----------|---------|
| GETTING_STARTED.md | Medium | 10 min | Step-by-step deployment |
| QUICK_START.md | Small | 3 min | Quick reference |
| ARCHITECTURE_CHANGES.md | Medium | 5 min | What changed |
| DEPLOYMENT_SUMMARY.md | Small | 3 min | Overview of changes |
| DEPLOYMENT_GUIDE.md | Large | 20 min | Comprehensive reference |
| FABRIC_NATIVE_ARCHITECTURE.md | Medium | 8 min | Technical design |
| OPENAPI_ARCHITECTURE.md | Medium | 8 min | API details |

---

## Next Steps

1. ✅ Read this file (you're doing it!)
2. 📖 Read `QUICK_START.md` (3 min)
3. ▶️ Follow `GETTING_STARTED.md` (30 min)
4. ✓ Validate using checklist (5 min)
5. 🚀 Deploy and test (ongoing)

---

## Status

- ✅ Code validated (15/15 checks)
- ✅ Architecture designed (Fabric-native)
- ✅ Documentation complete (7 guides)
- ✅ Ready to deploy
- ⏳ Waiting for your implementation

---

**Questions?** Start with the appropriate document above. Everything you need is here!
