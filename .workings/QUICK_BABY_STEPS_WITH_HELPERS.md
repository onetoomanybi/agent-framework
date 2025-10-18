# Baby Steps Guide with Gap-Aware Helpers
## Quick Start for Validation

This guide shows how to use **helper scripts** to validate each baby step quickly and accurately, with gap insights built in.

---

## 🚀 Quick Start: Run All Validations at Once

### Option 1: Python (Recommended)
```powershell
cd c:\repo\agent-framework\.workings

# Run all phases at once
python validation_helpers.py

# Or run specific phase
python validation_helpers.py 1  # Phase 1 only
python validation_helpers.py 3  # Phase 3 only
python validation_helpers.py 4  # Phase 4 only
python validation_helpers.py 5  # Phase 5 only
```

### Option 2: PowerShell
```powershell
cd c:\repo\agent-framework\.workings

# Run all phases at once
.\validation_helpers.ps1 -Phase all

# Or run specific phase
.\validation_helpers.ps1 -Phase 1
.\validation_helpers.ps1 -Phase 3
.\validation_helpers.ps1 -Phase 4
.\validation_helpers.ps1 -Phase 5
```

---

## 📋 What Each Helper Validates

### Phase 1: Fix Critical Issues (7 checks)
```powershell
python validation_helpers.py 1
```
Validates:
- ✅ Import guard for notebookutils (Gap #6)
- ✅ Mock credentials available (Gap #6)
- ✅ No hardcoded secrets (Gap #3)
- ✅ Azure AI Projects SDK v1.0.0+ (Gap #1)
- ✅ No deprecated connection_string (Gap #2)
- ✅ CSV parsing uses pandas (robust, not naive)
- ✅ Pagination parameters present (Gap #8)

**When to run**: Before Phase 1 submission
**Should pass**: 7/7 checks

---

### Phase 3: OpenAPI Specification (3 checks)
```powershell
python validation_helpers.py 3
```
Validates:
- ✅ Every operation has operationId (Gap #5 - CRITICAL for AI Agents Service)
- ✅ Only GET/POST methods present (Gap #9 - Azure AI Agents limitation)
- ✅ Server URL is accessible (not localhost) (Gap #7 - Spec hosting)

**When to run**: After updating openapi_spec.json
**Should pass**: 3/3 checks

---

### Phase 4: Resilience & Monitoring (3 checks)
```powershell
python validation_helpers.py 4
```
Validates:
- ✅ Retry logic implemented (Gap #8 - Handles transient failures)
- ✅ Logging configured (Gap #10 - Observability for debugging)
- ✅ Using GUIDs not names (Gap #12 - Immutable resource identifiers)

**When to run**: After Phase 4 implementation
**Should pass**: 3/3 checks

---

### Phase 5: Pre-Deployment (2 checks)
```powershell
python validation_helpers.py 5
```
Validates:
- ✅ Using Azure AI Agents Service (Gap #1 - Product clarity)
- ✅ OpenTelemetry configured (Gap #10 - Production observability)

**When to run**: Before deployment
**Should pass**: 2/2 checks

---

## 🎯 Manual Baby Steps (For Understanding)

If you want to understand what the helpers are checking, run these manual steps:

### Phase 1 - Manual Validation

**Step 1: Check Import Guard (Gap #6)**
```powershell
# Should show try/except block
Select-String -Path fabric_ai_foundry_client.py -Pattern "try:|except ImportError" -Context 2,2
```

**Step 2: Verify SDK Version (Gap #1)**
```powershell
# Should show version 1.x.x
pip show azure-ai-projects | Select-String "Version"
```

**Step 3: Check for Deprecated APIs (Gap #2)**
```powershell
# Should return NOTHING (deprecated pattern not present)
Select-String -Path fabric_ai_foundry_client.py -Pattern "from_connection_string"
```

**Step 4: Verify CSV Parsing (Robust)**
```powershell
# Should show pandas usage
Select-String -Path agent_lakehouse_tools.py -Pattern "pd\.read_csv"
```

### Phase 3 - Manual Validation

**Step 1: Check operationId (Gap #5 - CRITICAL)**
```powershell
# Every operation MUST have operationId for Azure AI Agents Service
$spec = Get-Content openapi_spec.json | ConvertFrom-Json
$spec.paths.PSObject.Properties | ForEach-Object {
    $_.Value.PSObject.Properties | ForEach-Object {
        if ($_.Value -is [PSCustomObject] -and -not $_.Value.operationId) {
            Write-Host "❌ Missing operationId on: $($_.Name)"
        }
    }
}
```

**Step 2: Check HTTP Methods (Gap #9)**
```powershell
# Should only find GET and POST
$spec = Get-Content openapi_spec.json | ConvertFrom-Json
$spec.paths.PSObject.Properties | ForEach-Object {
    $_.Value.PSObject.Properties | Where-Object { $_.Name -notin @("get", "post", "parameters") } | ForEach-Object {
        Write-Host "⚠️ Non-standard method: $($_.Name)"
    }
}
```

### Phase 4 - Manual Validation

**Step 1: Check Retry Logic (Gap #8)**
```powershell
# Should find retry or timeout keywords
Select-String -Path agent_lakehouse_tools.py -Pattern "retry|timeout" -Context 1,1
```

**Step 2: Check Logging (Gap #10)**
```powershell
# Should find logging configuration
Select-String -Path agent_lakehouse_tools.py -Pattern "import logging|logger\.info|logger\.debug" -Context 1,1
```

**Step 3: Check GUID Usage (Gap #12)**
```powershell
# Should find GUID patterns (not workspace_name or lakehouse_name)
Select-String -Path agent_lakehouse_tools.py -Pattern "[0-9a-f]{8}-[0-9a-f]{4}"
```

### Phase 5 - Manual Validation

**Step 1: Check Product Clarity (Gap #1)**
```powershell
# Should show azure-ai-projects (not agent-framework)
Select-String -Path requirements.txt -Pattern "azure-ai-projects"
```

**Step 2: Check Observability (Gap #10)**
```powershell
# Should show opentelemetry or azure-monitor
Select-String -Path requirements.txt -Pattern "opentelemetry|azure-monitor"
```

---

## 📊 Gap-to-Validation Mapping

| Gap # | Description | Phase | Helper Check | Manual Command |
|-------|-------------|-------|--------------|-----------------|
| #1 | Product Confusion | 1, 5 | `python validation_helpers.py 1` | `pip show azure-ai-projects` |
| #2 | Deprecated APIs | 1 | `python validation_helpers.py 1` | `Select-String -Path fabric_ai_foundry_client.py -Pattern "from_connection_string"` |
| #3 | Fabric Admin Settings | 1 | `python validation_helpers.py 1` | Manual prereq check in Fabric Admin |
| #5 | operationId Validation | 3 | `python validation_helpers.py 3` | PowerShell JSON parsing (see above) |
| #6 | Token Flow | 1 | `python validation_helpers.py 1` | Import guard + mock credential tests |
| #7 | Spec Hosting | 3 | `python validation_helpers.py 3` | Check server URL not localhost |
| #8 | Resilience/Retry | 4 | `python validation_helpers.py 4` | Grep for retry/timeout keywords |
| #9 | HTTP Methods | 3 | `python validation_helpers.py 3` | Check for GET/POST only |
| #10 | Observability | 4, 5 | `python validation_helpers.py 4` or `5` | Check logging imports |
| #12 | GUID Enforcement | 4 | `python validation_helpers.py 4` | Check for resource names |

---

## 🔍 Interpreting Results

### Successful Run
```
✅ Import guard present (try/except for notebookutils) (Gap #6)
✅ Mock credentials and FabricMLCredential class present (Gap #6)
✅ No hardcoded credentials found (Gap #3)
✅ Azure AI Projects SDK v1.0.0+ installed (Gap #1)
✅ Using modern endpoint + DefaultAzureCredential pattern (not deprecated connection_string) (Gap #2)
✅ CSV parsing uses pandas (not naive split)
✅ Pagination parameters (limit/offset) present (Gap #8)

=== PHASE 1 Summary: 7/7 checks passed ===
```

### Failed Check - How to Fix

**Example: Missing operationId (Gap #5)**
```
❌ Missing operationId on: get /listFiles (Gap #5)
```
**Fix**: Update `openapi_spec.json`:
```json
{
  "paths": {
    "/listFiles": {
      "get": {
        "operationId": "listFiles",  // ADD THIS
        "summary": "List files in lakehouse",
        ...
      }
    }
  }
}
```

**Example: Deprecated connection_string (Gap #2)**
```
❌ Deprecated from_connection_string() found (Gap #2)
```
**Fix**: Update `fabric_ai_foundry_client.py`:
```python
# BEFORE (deprecated)
client = AIProjectClient.from_connection_string(connection_string)

# AFTER (modern)
from azure.identity import DefaultAzureCredential
client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
    project_id=project_id
)
```

---

## 📝 Baby Step Completion Workflow

1. **Implement** the task (from BUILD_OUT_PROMPT.md)
2. **Run helper** to validate all checks at once
3. **Fix any failures** based on error messages
4. **Re-run helper** until all checks pass
5. **Mark task complete** in BUILD_OUT_PROMPT.md

Example:
```powershell
# Step 1: You implement Task 1.1 (import guard fix)

# Step 2: Run validation
python validation_helpers.py 1

# Step 3-4: If failures, fix them

# Step 5: Re-run
python validation_helpers.py 1

# Output shows: PHASE 1 Summary: 7/7 checks passed ✅
# Now you can move to next task
```

---

## 🆘 Troubleshooting

### Helper scripts not found
```powershell
# Make sure you're in correct directory
cd c:\repo\agent-framework\.workings

# Check files exist
Get-ChildItem validation_helpers.*
```

### Python helper fails to import
```powershell
# Make sure Python is in PATH
python --version

# Install required packages if needed
pip install azure-ai-projects azure-identity
```

### PowerShell execution policy error
```powershell
# Temporarily allow script execution
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Then run script
.\validation_helpers.ps1 -Phase 1
```

### Get-Content shows no output
```powershell
# Make sure file exists and has content
Get-Item fabric_ai_foundry_client.py | Select-Object FullName, Length

# Read first few lines
Get-Content fabric_ai_foundry_client.py -Head 10
```

---

## 📚 Reference: All Gap Numbers

- **Gap #1**: Product Confusion (Azure AI Agents Service vs Framework)
- **Gap #2**: Deprecated API Usage (from_connection_string)
- **Gap #3**: Fabric Admin Settings Missing
- **Gap #5**: operationId Requirement (CRITICAL for AI Agents)
- **Gap #6**: Authentication Token Flow
- **Gap #7**: OpenAPI Spec Hosting Strategy
- **Gap #8**: Resilience/Retry Logic
- **Gap #9**: HTTP Method Restrictions (GET/POST only)
- **Gap #10**: Observability/Monitoring
- **Gap #12**: GUID vs Name Enforcement

---

## ✅ Phase Readiness Checklist

### Ready for Phase 1 Submission?
```
✅ Run: python validation_helpers.py 1
✅ Result: 7/7 checks passed
✅ All imports work in Fabric AND locally
✅ No hardcoded secrets
✅ SDK methods verified
```

### Ready for Phase 3 Submission?
```
✅ Run: python validation_helpers.py 3
✅ Result: 3/3 checks passed
✅ operationId on every operation
✅ Only GET/POST methods
✅ Server URL accessible (not localhost)
```

### Ready for Phase 4 Submission?
```
✅ Run: python validation_helpers.py 4
✅ Result: 3/3 checks passed
✅ Retry logic implemented
✅ Logging configured
✅ Using GUIDs not names
```

### Ready for Phase 5 Submission?
```
✅ Run: python validation_helpers.py 5
✅ Result: 2/2 checks passed
✅ Azure AI Agents Service product confirmed
✅ OpenTelemetry configured
```

---

## 🎓 Learning Path

1. **Read** GAP_ANALYSIS_SUMMARY.md (understand what gaps exist)
2. **Read** BUILD_OUT_PROMPT.md (understand what to build)
3. **Implement** each task
4. **Run** helper scripts to validate
5. **Repeat** for each phase

The helpers make validation **fast, accurate, and gap-aware** - you know exactly why each check matters!
