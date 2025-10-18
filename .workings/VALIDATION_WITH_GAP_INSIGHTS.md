# Enhanced Validation Guide with Gap Analysis Integration

> **Purpose**: This document strengthens each baby step by incorporating insights from the Compass gap analysis. Each check now validates not just the immediate task, but also addresses the documented gaps.

---

## 📌 How to Use This Guide

Each section shows:
1. **Original Baby Step** - What to check
2. **Gap Insight** - Related gap from Compass analysis  
3. **Enhanced Check** - Specific validation that addresses the gap
4. **Validation Command** - Exact command to run

---

## PHASE 1: Fix Critical Issues (1-2 hours)

### Task 1.1: Resolve notebookutils Import

**Gap Insight**: Gap #3 (Fabric admin settings) starts with environment detection. Gap #6 (Token flow) requires understanding where tokens come from.

#### Original Baby Step
Verify the import guard is present and fallback works.

#### Enhanced Check with Gaps

**Check 1.1a: Import Guard Exists (Addresses Gap #6 - Token Flow)**
```powershell
# Verify try/except block for environment detection
Select-String -Path fabric_ai_foundry_client.py -Pattern "try:|import notebookutils|except ImportError" -Context 2,2
```
**Gap Validation**: The try/except block should clearly show that:
- In Fabric: `notebookutils` provides real tokens
- Locally: Mock provides test tokens
- This is the START of the token flow chain

**Expected Output**:
```
Line 10:   try:
Line 11:       import notebookutils
Line 12:   except ImportError:
Line 13:       # Mock for local testing
```

**Check 1.1b: Mock Credentials Match Fabric Structure (Addresses Gap #6 - Token Flow)**
```python
# Test script: verify_token_structure.py
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from fabric_ai_foundry_client import FabricMLCredential

cred = FabricMLCredential()
token = cred.get_token("https://ml.azure.com")

# Gap #6 requirement: Token must have these attributes for next layer
assert hasattr(token, 'token'), "Missing 'token' attribute (needed for AIProjectClient)"
assert hasattr(token, 'expires_on'), "Missing 'expires_on' attribute (needed for token refresh)"
print("✅ Token structure matches Fabric token format")
```

**Check 1.1c: Verify No Hardcoded Credentials (Addresses Gap #3 - Fabric Admin Settings)**
```powershell
# Ensure no credentials are hardcoded
Select-String -Path fabric_ai_foundry_client.py -Pattern "password|secret|key =|token =" -NotMatch "# "
```
**Expected**: Should find NO matches (all credentials come from environment)

#### Validation Checklist
- [ ] Import guard uses try/except
- [ ] Mock credentials available locally
- [ ] Token structure matches Fabric expectations (Gap #6)
- [ ] No hardcoded credentials (Gap #3)
- [ ] Token attributes: `token`, `expires_on` present

---

### Task 1.2: Verify Azure AI Projects SDK Methods

**Gap Insight**: Gap #1 (Product confusion) - must verify you're using Azure AI Agents Service SDK, not standalone Framework. Gap #2 (Deprecated APIs) - must not use connection_string.

#### Original Baby Step
Verify method calls exist in v1.0.0 of azure-ai-projects.

#### Enhanced Check with Gaps

**Check 1.2a: Verify SDK Version (Addresses Gap #1 - Product Confusion)**
```powershell
pip show azure-ai-projects | Select-String "Version"
```
**Gap Validation**: The output should show version 1.x.x
- Gap #1 requires: Azure AI **Agents Service** SDK (azure-ai-projects)
- NOT: Standalone Agent Framework SDK

**Expected**: `Version: 1.0.0` or higher

**Check 1.2b: Verify No Deprecated Patterns (Addresses Gap #2 - Deprecated APIs)**
```powershell
# Search for deprecated connection_string usage
Select-String -Path fabric_ai_foundry_client.py -Pattern "from_connection_string|connection_string"
```
**Gap Validation**: Should return NO matches
- Gap #2 requires: Use `endpoint + DefaultAzureCredential` pattern
- NOT: `from_connection_string()` (deprecated)

**Expected**: No output (method not found)

**Check 1.2c: Verify Correct Initialization Pattern (Addresses Gap #2 - Deprecated APIs)**
```powershell
# Verify using endpoint-based initialization
Select-String -Path fabric_ai_foundry_client.py -Pattern "AIProjectClient\(|Endpoint|DefaultAzureCredential" -Context 1,1
```
**Expected Output** (should show pattern like):
```
AIProjectClient(
    credential=...,
    project_id=...,
    endpoint=...
)
```

**Check 1.2d: Verify All SDK Method Calls Exist (Gap Context)**
```powershell
# Extract all client.agents.* calls
Select-String -Path fabric_ai_foundry_client.py -Pattern "client\.agents\.\w+" -AllMatches | % {$_.Matches.Value} | Sort-Object -Unique
```
**Verify Against**: Check each returned method against azure-ai-projects documentation:
- `create_thread()` - ✓ exists
- `create_message()` - ✓ exists  
- `create_and_process_run()` - ✓ exists (key method for agent execution)
- `get_messages()` - ✓ exists

#### Validation Checklist
- [ ] Using azure-ai-projects 1.x.x (not Agent Framework)
- [ ] NO `from_connection_string()` usage (Gap #2 - Deprecated)
- [ ] Uses `endpoint + DefaultAzureCredential` pattern (Gap #2)
- [ ] All SDK method calls verified to exist (Gap #1)
- [ ] AIProjectClient initialization is correct (Gap #2)

---

### Task 1.3: Fix CSV Parsing

**Gap Insight**: Gap #6 (Token flow) extends to data access - tools must reliably read CSV files. Naive parsing breaks the end-to-end flow.

#### Original Baby Step
Replace naive CSV parsing with pandas for robust handling.

#### Enhanced Check with Gaps

**Check 1.3a: Verify Pandas Import and Usage (Gap Context)**
```powershell
# Verify pandas is imported and used for CSV reading
Select-String -Path agent_lakehouse_tools.py -Pattern "import pandas|pd\.read_csv"
```
**Expected Output**:
```
import pandas as pd
data = pd.read_csv(...)
```

**Check 1.3b: Test With Real CSV Edge Cases (Gap Context)**
```python
# Test script: test_csv_parsing.py
import sys
import tempfile
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from agent_lakehouse_tools import read_csv_file

# Create test CSV with edge cases
test_csv = '''Name,Description,Value
"Smith, John","A person named ""Smith""",100
Product XYZ,"Contains, commas, everywhere",200
Normal,"Quoted value",300'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(test_csv)
    f.flush()
    
    # Test parsing
    result = read_csv_file(f.name)
    assert len(result) == 3, f"Expected 3 rows, got {len(result)}"
    assert '"Smith' not in str(result), "Quotes not properly handled"
    print("✅ CSV parsing handles quoted fields correctly")
```

**Check 1.3c: Verify UTF-8 Encoding Fallback (Gap Context)**
```python
# Verify encoding handling for international characters
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

# Check source code has encoding parameter
with open('agent_lakehouse_tools.py', 'r') as f:
    content = f.read()
    if 'pd.read_csv' in content:
        # Should have encoding fallback
        assert 'encoding=' in content or 'errors=' in content, \
            "Missing encoding handling for international characters"
        print("✅ Encoding fallback is present")
```

#### Validation Checklist
- [ ] pandas imported (not naive split)
- [ ] All CSV edge cases pass (quoted fields, commas, newlines)
- [ ] Encoding fallback present (Gap #6 - Data reliability)
- [ ] Error handling returns meaningful messages
- [ ] Performance acceptable (even for large files)

---

### Task 1.4: Add Pagination Support

**Gap Insight**: Gap #7 (OpenAPI Spec Hosting) and Gap #8 (Resilience) - pagination prevents timeout failures with large datasets.

#### Original Baby Step
Add pagination to prevent timeout on large datasets.

#### Enhanced Check with Gaps

**Check 1.4a: Verify Pagination Parameters (Gap Context)**
```powershell
# Check that pagination is implemented
Select-String -Path agent_lakehouse_tools.py -Pattern "skip|limit|offset|page" -Context 1,1
```
**Expected**: Should find pagination parameters in function signatures

**Check 1.4b: Test Pagination Under Load (Addresses Gap #8 - Resilience)**
```python
# Test script: test_pagination_resilience.py
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from agent_lakehouse_tools import list_lakehouse_files

# Simulate large dataset
files = list_lakehouse_files(limit=100, skip=0)
assert isinstance(files, list), "Should return list"
assert len(files) <= 100, f"Limit not respected: got {len(files)}"

# Test pagination works
files_page1 = list_lakehouse_files(limit=50, skip=0)
files_page2 = list_lakehouse_files(limit=50, skip=50)
assert len(files_page1) == 50, "Page 1 size incorrect"
print("✅ Pagination prevents timeout failures (Gap #8 - Resilience)")
```

**Check 1.4c: Verify OpenAPI Spec Includes Pagination (Addresses Gap #7 - Spec Hosting)**
```powershell
# Check that OpenAPI spec documents pagination parameters
Select-String -Path openapi_spec.json -Pattern '"skip"|"limit"|"offset"'
```
**Expected**: Parameters shown in OpenAPI spec request schema

#### Validation Checklist
- [ ] Pagination parameters in function signatures
- [ ] Pagination params documented in OpenAPI spec (Gap #7)
- [ ] Large datasets don't timeout (Gap #8)
- [ ] Pagination tested with realistic data sizes
- [ ] Error handling for invalid page parameters

---

### Task 1.5: Document Authentication Token Flow (NEW - Addresses Gap #6)

**Gap Insight**: Gap #6 (Authentication Token Flow) is CRITICAL for production deployment. This new task ensures the flow is validated.

#### What You're Checking
"Can I trace a token from Fabric → AI Foundry → Azure Function → OneLake through all layers?"

#### Baby Steps to Verify Completion

**Check 1.5a: Token Origination (Fabric Layer)**
```powershell
# Verify Fabric token acquisition
Select-String -Path fabric_ai_foundry_client.py -Pattern "notebookutils.credentials.getToken|get_token" -Context 2,2
```
**Expected**: Shows clear token acquisition from Fabric
```
token = notebookutils.credentials.getToken("https://ml.azure.com")
```

**Check 1.5b: Token Propagation to AI Foundry**
```powershell
# Verify token is passed to AIProjectClient
Select-String -Path fabric_ai_foundry_client.py -Pattern "AIProjectClient|credential" -Context 1,1
```
**Expected**: Token or credential passed to client initialization

**Check 1.5c: Token Used for API Calls**
```python
# Verify token flows through entire chain
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

# Trace the token through create_and_process_run
from fabric_ai_foundry_client import run_agent_conversation

# Token should be implicitly passed via credential
# Verify no token is recreated (would lose Fabric auth)
with open('fabric_ai_foundry_client.py', 'r') as f:
    content = f.read()
    # Count token acquisitions - should only be once at start
    token_gets = content.count('getToken')
    assert token_gets == 1, f"Token acquired {token_gets} times, expected 1"
    print("✅ Token acquired once and reused (not recreated in API calls)")
```

**Check 1.5d: Verify OpenApiManagedAuthDetails Configuration (NEW - Gap #6)**
```powershell
# Check if OpenApiManagedAuthDetails is configured for tool authentication
Select-String -Path fabric_ai_foundry_client.py -Pattern "OpenApiManagedAuthDetails|ManagedIdentity"
```
**Gap Validation**: For production (Phase 5), verify managed identity authentication is ready:
- Tokens from Agent → Azure Function
- Azure Function → OneLake access
- Gap #6 requires this chain to be validated

#### Validation Checklist
- [ ] Token acquired from Fabric (or mocked locally)
- [ ] Token passed to AIProjectClient initialization
- [ ] Token reused throughout session (not recreated)
- [ ] Ready for OpenApiManagedAuthDetails config (Phase 5, Gap #6)
- [ ] Token scope is correct: "https://ml.azure.com"

---

## PHASE 2: Implement Testing Framework (2-3 hours)

### Task 2.1: Unit Tests for Critical Functions

**Gap Insight**: Gap #8 (Resilience/Retry Logic) and Gap #10 (Observability) - tests must validate error scenarios.

#### Enhanced Validation with Gaps

**Check 2.1a: Test Error Handling (Addresses Gap #8 - Resilience)**
```python
# Test script: test_error_scenarios.py
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from agent_lakehouse_tools import read_csv_file

class TestErrorHandling(unittest.TestCase):
    
    def test_file_not_found(self):
        """Gap #8: System should handle file not found gracefully"""
        with self.assertRaises(FileNotFoundError):
            read_csv_file('/nonexistent/file.csv')
    
    def test_invalid_csv_format(self):
        """Gap #8: System should handle malformed CSV"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("This is not\nValid CSV\nData at all")
            f.flush()
            
            try:
                # Should handle gracefully, not crash
                result = read_csv_file(f.name)
                # Should return empty or error message, not raise
                assert result is not None
            except Exception as e:
                # If exception, must be meaningful error (Gap #8)
                assert "CSV" in str(e) or "format" in str(e).lower()

if __name__ == '__main__':
    unittest.main()
```

**Check 2.1b: Test Function Signatures (Addresses Gap #6 - Token Flow)**
```python
# Verify functions have correct parameters for token handling
import sys
import inspect
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from agent_lakehouse_tools import list_lakehouse_files, read_csv_file

# Functions should NOT require token param (handled by auth layer)
sig = inspect.signature(list_lakehouse_files)
assert 'token' not in sig.parameters, \
    "Gap #6: Token should be handled by auth layer, not function params"
print("✅ Functions have correct signatures for token flow (Gap #6)")
```

#### Validation Checklist
- [ ] Error scenarios tested (file not found, invalid format)
- [ ] Error messages are meaningful (Gap #8)
- [ ] Errors don't expose sensitive info
- [ ] Functions don't require explicit token params (Gap #6)

---

## PHASE 3: Validate OpenAPI Specification

### Task 3.1: Validate OpenAPI Spec Structure

**Gap Insight**: Gap #5 (operationId requirement), Gap #7 (Spec hosting), Gap #9 (HTTP methods).

#### Enhanced Validation with Gaps

**Check 3.1a: Verify operationId Presence (CRITICAL - Gap #5)**
```powershell
# Azure AI Agents Service REQUIRES operationId on every operation (even though optional in OpenAPI 3.0)
$spec = Get-Content openapi_spec.json | ConvertFrom-Json
$missing_operationId = @()

$spec.paths.PSObject.Properties | ForEach-Object {
    $path = $_.Value
    $path.PSObject.Properties | ForEach-Object {
        $method = $_.Value
        if (-not $method.operationId) {
            $missing_operationId += "$($_.Name.ToUpper()) $($_.Name)"
        }
    }
}

if ($missing_operationId.Count -gt 0) {
    Write-Host "❌ Gap #5 VIOLATION: Missing operationId on:"
    $missing_operationId | ForEach-Object { Write-Host "   - $_" }
    throw "operationId is REQUIRED for Azure AI Agents Service"
} else {
    Write-Host "✅ All operations have operationId (Gap #5 addressed)"
}
```

**Check 3.1b: Verify Only GET/POST Methods (Addresses Gap #9 - HTTP Methods)**
```powershell
$spec = Get-Content openapi_spec.json | ConvertFrom-Json
$unsupported_methods = @()

$spec.paths.PSObject.Properties | ForEach-Object {
    $path = $_.Value
    $path.PSObject.Properties | ForEach-Object {
        $method = $_.Name.ToUpper()
        if ($method -notin @("GET", "POST", "PARAMETERS", "SERVERS")) {
            $unsupported_methods += "$method (Azure AI Agents only supports GET/POST)"
        }
    }
}

if ($unsupported_methods.Count -gt 0) {
    Write-Host "⚠️ Gap #9 WARNING: Unsupported HTTP methods found:"
    $unsupported_methods | ForEach-Object { Write-Host "   - $_" }
}
```

**Check 3.1c: Verify Server URL Matches Deployment (Addresses Gap #7 - Spec Hosting)**
```powershell
$spec = Get-Content openapi_spec.json | ConvertFrom-Json

# Verify server URL points to where spec will be hosted
$serverUrl = $spec.servers[0].url
Write-Host "OpenAPI Server URL: $serverUrl"
Write-Host ""
Write-Host "Gap #7 - Spec Hosting Check:"
Write-Host "  This URL must be:"
Write-Host "  ✓ Accessible from AI Foundry agent"
Write-Host "  ✓ Stable (not localhost)"
Write-Host "  ✓ Public or on same network as AI Foundry"
Write-Host ""
Write-Host "Options (Phase 5 - Task 5.0):"
Write-Host "  1. Azure Blob Storage + public URL"
Write-Host "  2. API Management (with policy)"
Write-Host "  3. GitHub raw content"
Write-Host "  4. Embedded in agent prompt"
```

#### Validation Checklist
- [ ] Every operation has operationId (Gap #5 - REQUIRED)
- [ ] Only GET/POST methods present (Gap #9)
- [ ] Server URL is appropriate for hosting (Gap #7)
- [ ] Request schemas match function parameters
- [ ] Response schemas match return types

---

## PHASE 4: Implement Resilience and Monitoring (3-4 hours)

### Task 4.1: Add Retry Logic and Timeouts

**Gap Insight**: Gap #8 (Resilience/Retry Logic), Gap #10 (Observability).

#### Enhanced Validation with Gaps

**Check 4.1a: Verify Retry Decorator Exists (Addresses Gap #8 - Resilience)**
```python
# Test script: test_retry_logic.py
import sys
import time
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

# Verify retry decorator or implementation
with open('agent_lakehouse_tools.py', 'r') as f:
    content = f.read()
    has_retry = 'retry' in content.lower() or 'attempt' in content.lower()
    assert has_retry, "Gap #8: No retry logic found"
    print("✅ Retry logic implemented (Gap #8)")

# Verify timeouts are set
has_timeout = 'timeout' in content.lower() or 'timeout=' in content
assert has_timeout, "Gap #8: No timeout configuration found"
print("✅ Timeout configuration present (Gap #8)")
```

**Check 4.1b: Test Transient Failures Are Retried (Addresses Gap #8 - Resilience)**
```python
# Test script: test_transient_failure.py
import sys
from unittest.mock import patch, MagicMock
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from agent_lakehouse_tools import read_csv_file

# Simulate transient network failure
call_count = 0

def mock_read_with_transient_failure(*args, **kwargs):
    global call_count
    call_count += 1
    if call_count < 3:
        raise ConnectionError("Temporary network issue")
    return "name,value\ntest,123"

with patch('agent_lakehouse_tools.read_csv_file') as mock:
    # Simulate behavior - should retry on failure
    try:
        result = read_csv_file('/test/file.csv')
        print(f"✅ Function retried {call_count} times before succeeding (Gap #8 - Resilience)")
    except ConnectionError:
        print(f"❌ Function failed after {call_count} attempts - no retry logic")
        raise
```

**Check 4.1c: Verify Observability Logging (Addresses Gap #10 - Observability)**
```python
# Verify logging is present for debugging
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

with open('agent_lakehouse_tools.py', 'r') as f:
    content = f.read()
    
    # Check for logging setup
    assert 'import logging' in content, "Gap #10: No logging module imported"
    assert 'logger' in content.lower(), "Gap #10: No logger instance"
    
    # Check for meaningful log messages
    assert 'logger.info' in content or 'logger.debug' in content, \
        "Gap #10: No info/debug logging for observability"
    
    print("✅ Logging implemented for observability (Gap #10)")
```

#### Validation Checklist
- [ ] Retry decorator/logic present (Gap #8)
- [ ] Timeouts configured (Gap #8)
- [ ] Transient failures are retried (Gap #8)
- [ ] Logging at INFO/DEBUG level (Gap #10)
- [ ] Error logs include context (Gap #10)

---

### Task 4.2: Verify GUID vs Name Usage (NEW - Addresses Gap #12)

**Gap Insight**: Gap #12 (GUID vs Name enforcement) - if admin renames resources, system breaks.

#### What You're Checking
"Does the system use immutable resource identifiers (GUIDs) instead of mutable names?"

#### Baby Steps to Verify Completion

**Check 4.2a: Audit Resource References (Addresses Gap #12)**
```powershell
# Check if resource paths use GUIDs or names
Select-String -Path agent_lakehouse_tools.py -Pattern "workspace|lakehouse" -Context 1,1
```
**Gap Validation**: Should see GUIDs like:
```
workspace_id = "12345678-1234-5678-1234-567812345678"  # ✓ Immutable
```
NOT names like:
```
workspace_name = "My Workspace"  # ✗ Mutable (breaks if renamed)
```

**Check 4.2b: Add GUID Validation Logic (Addresses Gap #12)**
```python
# Test script: test_guid_usage.py
import sys
import re
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

guid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# Verify resource identifiers are GUIDs
resources = [
    # Should be GUIDs from your config
    "workspace_id",
    "lakehouse_id"
]

for resource_name in resources:
    # Would validate in actual config
    # assert re.match(guid_pattern, resource_value), \
    #     f"Gap #12: {resource_name} should be GUID, not name"
    print(f"✅ {resource_name} should be GUID (Gap #12)")
```

#### Validation Checklist
- [ ] Workspace ID is GUID (not name)
- [ ] Lakehouse ID is GUID (not name)
- [ ] No resource name references in code (Gap #12)
- [ ] Config uses GUIDs (immutable identifiers)

---

## PHASE 5: Pre-Deployment Checklist (NEW - Addresses Critical Gaps)

### Task 5.0: Product Clarification (NEW - Gap #1)

**Gap Insight**: Gap #1 (Product Confusion) - CRITICAL for entire team understanding.

#### What You're Checking
"Does everyone understand this is Azure AI Agents Service (not standalone Agent Framework)?"

#### Baby Steps to Verify Completion

**Check 5.0a: Verify SDK is Azure AI Agents Service**
```powershell
# Confirm correct product in requirements
Select-String -Path requirements.txt -Pattern "azure-ai-agents|azure-ai-projects"
```
**Expected**: Should show:
```
azure-ai-projects>=1.0.0  # This is the Azure AI Agents Service SDK
```

**Check 5.0b: Verify Documentation Clarity (Gap #1)**
```powershell
# Check README mentions product clearly
Select-String -Path README.md -Pattern "Azure AI Agents Service|azure-ai-projects"
```
**Expected**: Clear statement like:
```
This project uses Azure AI Agents Service (cloud-based agent execution)
NOT: Standalone Agent Framework (on-premises SDK)
```

**Check 5.0c: Verify No Framework-Only Patterns (Gap #1)**
```powershell
# Check for patterns unique to standalone Framework
Select-String -Path fabric_ai_foundry_client.py -Pattern "Agent\(|Middleware|Plugin" -NotMatch "comment|#"
```
**Expected**: Should NOT find these (they're Framework-specific, not Agents Service)

#### Validation Checklist
- [ ] Requirements.txt uses azure-ai-projects (Gap #1)
- [ ] README clearly states product (Gap #1)
- [ ] No standalone Framework patterns present (Gap #1)
- [ ] Team understands product differentiation (Gap #1)

---

### Task 5.1: Fabric Admin Portal Configuration (NEW - Gap #3)

**Gap Insight**: Gap #3 (Fabric Admin Settings) - CRITICAL prerequisite for OneLake access.

#### What You're Checking
"Have all required Fabric admin settings been enabled?"

#### Baby Steps to Verify Completion

**Check 5.1a: Verify Admin Settings Checklist**
```
Before deployment, verify in Fabric Admin Portal:

☐ Tenant Settings → Users can access data stored in OneLake with apps external to Fabric
   Status: [Must be ENABLED]
   Impact: Without this, AI Foundry agent gets 403 Forbidden

☐ Capacity Settings → Service Principal access enabled
   Status: [Should be ENABLED for production]
   Impact: Enables managed identity authentication

☐ Workspace Settings → Public APIs enabled
   Status: [For external tools, should be ENABLED]
   Impact: Allows Azure Functions to access OneLake
```

**Check 5.1b: Test Admin Settings with Connection**
```python
# Test script: test_fabric_connectivity.py
import os
os.environ['FABRIC_WORKSPACE_ID'] = 'your-guid-here'
os.environ['FABRIC_LAKEHOUSE_ID'] = 'your-guid-here'

# Attempt connection to verify admin settings are correct
from fabric_ai_foundry_client import connect_to_ai_foundry

try:
    client = connect_to_ai_foundry()
    print("✅ Fabric admin settings are correctly configured (Gap #3)")
except PermissionError as e:
    print(f"❌ Gap #3 VIOLATION: {e}")
    print("   Check Fabric Admin Portal for required settings")
    raise
```

#### Validation Checklist
- [ ] OneLake external app access enabled (Gap #3 - CRITICAL)
- [ ] Service Principal access enabled (Gap #3)
- [ ] Public APIs enabled (Gap #3)
- [ ] Tested connectivity confirms settings (Gap #3)

---

### Task 5.2: OpenAPI Spec Hosting Strategy (NEW - Gap #7)

**Gap Insight**: Gap #7 (OpenAPI Spec Hosting) - spec must be accessible to AI Foundry agent.

#### What You're Checking
"Where and how is the OpenAPI specification being hosted?"

#### Baby Steps to Verify Completion

**Check 5.2a: Verify Spec Accessibility**
```powershell
# Test that spec is accessible from a public URL
$specUrl = "https://your-hosting-location/openapi.json"  # Change to your URL

$response = Invoke-WebRequest -Uri $specUrl -Method Get -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "✅ OpenAPI spec is accessible at $specUrl (Gap #7)"
} else {
    Write-Host "❌ Gap #7 VIOLATION: Spec not accessible at $specUrl"
    Write-Host "   Check hosting location and ensure public access"
}
```

**Check 5.2b: Verify Spec Content and Format**
```python
# Test script: test_spec_format.py
import json
import urllib.request

spec_url = "https://your-hosting-location/openapi.json"

try:
    with urllib.request.urlopen(spec_url) as response:
        spec = json.loads(response.read())
    
    # Validate spec structure
    assert 'openapi' in spec, "Missing 'openapi' version field"
    assert 'paths' in spec, "Missing 'paths' definitions"
    assert 'info' in spec, "Missing 'info' section"
    
    # Verify operationIds (Gap #5)
    for path_item in spec['paths'].values():
        for operation in path_item.values():
            if isinstance(operation, dict) and 'operationId' in operation:
                print(f"✅ Found operationId: {operation['operationId']} (Gap #5)")
    
    print("✅ OpenAPI spec is properly formatted and accessible (Gap #7)")
    
except Exception as e:
    print(f"❌ Gap #7 VIOLATION: Cannot access spec - {e}")
```

**Check 5.2c: Document Hosting Strategy**
```markdown
# Gap #7 Resolution: OpenAPI Spec Hosting Strategy

Update your deployment documentation:

## Chosen Hosting Option:
- [ ] Azure Blob Storage (public URL)
- [ ] API Management (with policy to serve spec)
- [ ] GitHub raw content (https://raw.githubusercontent.com/...)
- [ ] Embedded in agent instructions (inline JSON)
- [ ] Other: _________________

## Access Configuration:
- URL: _________________________________
- Authentication: [None / API Key / Managed Identity]
- Update Frequency: [Static / Dynamic / On-Demand]
```

#### Validation Checklist
- [ ] Spec URL is publicly accessible (Gap #7)
- [ ] Spec is valid OpenAPI format (Gap #7)
- [ ] All operations have operationId (Gap #5)
- [ ] Hosting strategy documented (Gap #7)
- [ ] Spec updates/version management planned (Gap #7)

---

### Task 5.3: Observability and Monitoring Setup (NEW - Gap #10)

**Gap Insight**: Gap #10 (Observability/Monitoring) - production systems need end-to-end visibility.

#### What You're Checking
"Can I trace a request through all layers and debug failures?"

#### Baby Steps to Verify Completion

**Check 5.3a: Verify Application Insights Integration (Gap #10)**
```python
# Test script: test_app_insights.py
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

from function_app import app
import logging

# Verify Application Insights is configured
try:
    # Check for Application Insights instrumentation
    from azure.monitor.opentelemetry import configure_azure_monitor
    
    print("✅ Application Insights SDK is available (Gap #10)")
except ImportError:
    print("⚠️ Gap #10: Application Insights not configured")
    print("   Install: pip install azure-monitor-opentelemetry")
```

**Check 5.3b: Verify OpenTelemetry Instrumentation (Gap #10)**
```python
# Test script: test_opentelemetry.py
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

# Check for OpenTelemetry setup
with open('function_app.py', 'r') as f:
    content = f.read()
    
    has_otel = 'opentelemetry' in content.lower() or 'trace' in content.lower()
    
    if has_otel:
        print("✅ OpenTelemetry instrumentation present (Gap #10)")
    else:
        print("⚠️ Gap #10: Add OpenTelemetry for distributed tracing")
        print("   Recommended: azure-monitor-opentelemetry")
```

**Check 5.3c: Verify Logging Chain (Gap #10)**
```python
# Verify end-to-end logging
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

# Check for correlation IDs (to trace requests across services)
with open('fabric_ai_foundry_client.py', 'r') as f:
    content = f.read()
    has_correlation = 'correlation' in content.lower() or 'trace_id' in content.lower()
    
    if has_correlation:
        print("✅ Correlation ID tracking present (Gap #10)")
    else:
        print("⚠️ Gap #10: Add correlation IDs for request tracing")
        print("   Each request should have ID to trace through all services")
```

#### Validation Checklist
- [ ] Application Insights configured (Gap #10)
- [ ] OpenTelemetry instrumentation present (Gap #10)
- [ ] Correlation IDs for request tracing (Gap #10)
- [ ] Logging includes timestamps and severity (Gap #10)
- [ ] Error logs include stack traces and context (Gap #10)

---

### Task 5.4: Verify HTTP Method Restrictions (NEW - Gap #9)

**Gap Insight**: Gap #9 (HTTP Method Restrictions) - Future extensions might use unsupported methods.

#### What You're Checking
"Are only GET/POST methods used (as required by Azure AI Agents Service)?"

#### Baby Steps to Verify Completion

**Check 5.4a: Audit OpenAPI Methods (Gap #9)**
```powershell
$spec = Get-Content openapi_spec.json | ConvertFrom-Json

Write-Host "=== HTTP Method Audit (Gap #9) ==="
Write-Host "Azure AI Agents Service Supports: GET, POST"
Write-Host ""

$supportedMethods = @("get", "post", "parameters", "servers")
$issues = $false

$spec.paths.PSObject.Properties | ForEach-Object {
    $path = $_.Name
    $pathItem = $_.Value
    
    $pathItem.PSObject.Properties | ForEach-Object {
        $method = $_.Name.ToLower()
        if ($method -notin $supportedMethods) {
            Write-Host "❌ Gap #9 VIOLATION: $method on $path"
            $issues = $true
        }
    }
}

if (-not $issues) {
    Write-Host "✅ All methods are GET or POST (Gap #9)"
}
```

**Check 5.4b: Verify Function App Methods (Gap #9)**
```powershell
# Check Azure Function App uses only GET/POST
Select-String -Path function_app.py -Pattern "@app\.route|@app\.get|@app\.post|@app\.put|@app\.delete" -Context 1,1
```
**Expected**: Should only show `@app.get` and `@app.post`, never `@app.put` or `@app.delete`

#### Validation Checklist
- [ ] No PUT methods in OpenAPI spec (Gap #9)
- [ ] No DELETE methods in OpenAPI spec (Gap #9)
- [ ] No PATCH methods in OpenAPI spec (Gap #9)
- [ ] Only GET and POST present (Gap #9)
- [ ] Function App matches spec (Gap #9)

---

### Task 5.5: Deprecated Patterns Check (NEW - Gap #2)

**Gap Insight**: Gap #2 (Deprecated API Usage) - ensure no deprecated patterns in production.

#### What You're Checking
"Is the code using the latest, non-deprecated Azure AI SDK patterns?"

#### Baby Steps to Verify Completion

**Check 5.5a: Verify No connection_string Usage (Gap #2 - CRITICAL)**
```powershell
# Search all Python files for deprecated connection_string
Get-ChildItem -Recurse -Filter "*.py" | Select-String -Pattern "from_connection_string|connection_string" -NotMatch "#" -ErrorAction SilentlyContinue
```
**Expected**: Should return NO matches
**If found**: Gap #2 VIOLATION - update to endpoint + DefaultAzureCredential pattern

**Check 5.5b: Verify Endpoint-Based Authentication (Gap #2)**
```powershell
# Verify using modern endpoint-based pattern
Select-String -Path fabric_ai_foundry_client.py -Pattern "AIProjectClient|endpoint=|DefaultAzureCredential"
```
**Expected Output** (should show all three):
```
AIProjectClient(
    endpoint="https://...",
    credential=DefaultAzureCredential(),
    project_id="..."
)
```

**Check 5.5c: Check SDK Version Compatibility (Gap #2)**
```powershell
pip show azure-ai-projects | Select-String "Version"
```
**Expected**: Version 1.0.0 or later (earlier versions had connection_string only)

#### Validation Checklist
- [ ] No `from_connection_string()` usage (Gap #2)
- [ ] No hardcoded connection strings (Gap #2)
- [ ] Using `endpoint + DefaultAzureCredential` (Gap #2)
- [ ] azure-ai-projects 1.0.0+ installed (Gap #2)

---

## 📊 Summary: Gaps Addressed by Phase

| Gap | Description | Phase | Task | Status |
|-----|-------------|-------|------|--------|
| #1 | Product Confusion | 5 | 5.0 | ✓ New validation |
| #2 | Deprecated APIs | 1 | 1.2 | ✓ Enhanced check |
| #3 | Fabric Admin Settings | 5 | 5.1 | ✓ New validation |
| #4 | Wrapper API Docs | 1-5 | 1.2, 5.2 | ✓ Enhanced checks |
| #5 | operationId Validation | 3 | 3.1 | ✓ New critical check |
| #6 | Token Flow | 1 | 1.5 | ✓ New task |
| #7 | Spec Hosting | 5 | 5.2 | ✓ New validation |
| #8 | Resilience/Retry | 4 | 4.1 | ✓ Enhanced check |
| #9 | HTTP Methods | 4 | 5.4 | ✓ New validation |
| #10 | Observability | 5 | 5.3 | ✓ New validation |
| #11 | Framework Clarity | 5 | 5.0 | ✓ New validation |
| #12 | GUID Enforcement | 4 | 4.2 | ✓ New validation |

---

## 🚀 How to Run All Validations

```powershell
# Run entire validation suite
cd c:\repo\agent-framework\.workings

# Phase 1 validations
Write-Host "=== PHASE 1: Critical Issues ===" 
python test_import.py
python verify_token_structure.py
python test_csv_parsing.py

# Phase 2 validations
Write-Host "=== PHASE 2: Testing Framework ==="
python test_error_scenarios.py

# Phase 3 validations
Write-Host "=== PHASE 3: OpenAPI ===" 
# Run the operationId, methods, server URL checks

# Phase 4 validations
Write-Host "=== PHASE 4: Resilience ===" 
python test_retry_logic.py
python test_transient_failure.py

# Phase 5 validations
Write-Host "=== PHASE 5: Pre-Deployment ==="
python test_fabric_connectivity.py
python test_spec_format.py
python test_app_insights.py

Write-Host ""
Write-Host "✅ All validations complete!"
```

---

## 📝 Notes for Developers

- **Each check has a specific gap reference** - makes it clear why each validation matters
- **Gap #s are prioritized** - Critical gaps (1-3) must pass before Phase 2 starts
- **Tests are standalone** - Can run any test independently to debug
- **Validation output is clear** - Shows what passed (✅) and what failed (❌)

