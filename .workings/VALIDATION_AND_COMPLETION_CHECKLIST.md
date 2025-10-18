# Validation & Completion Checklist
## Baby Developer Steps for Each Phase

This guide shows **exactly how to check** that each phase is complete using baby developer steps - simple, clear, testable actions.

---

## 🎯 Overall Strategy

**Every task has**:
1. **What to do** - The implementation
2. **Acceptance criteria** - When it's done
3. **How to verify** - Concrete baby steps to check completion

---

## PHASE 1: Fix Critical Issues ✅

### Task 1.1: Resolve notebookutils Import

#### What You're Checking
"Can the code run in BOTH Fabric AND local test environments?"

#### Baby Steps to Verify Completion

**Step 1: Import Check**
```powershell
# Navigate to project
cd c:\repo\agent-framework\.workings

# Check the import block exists
Get-Content fabric_ai_foundry_client.py -Head 40 | Select-String -Pattern "try:|notebookutils|except ImportError"
```
**What to expect**: See try/except block with both paths

**Step 2: Local Import Test**
```python
# Create simple test file: test_import.py
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

try:
    from fabric_ai_foundry_client import FabricMLCredential
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
```

**Step 3: Token Object Test**
```python
# Test that mock works
credential = FabricMLCredential()
token = credential.get_token("https://ml.azure.com")
print(f"Token exists: {token is not None}")
print(f"Has attributes: {hasattr(token, 'token')}")
```

**Step 4: Visual Verification**
Open `fabric_ai_foundry_client.py` and verify:
```
✓ Lines 1-15: Has try/except for notebookutils
✓ Lines 16-25: Has MockNotebookUtils class definition
✓ Lines 26-35: Has FabricMLCredential.get_token() method
✓ No bare `notebookutils` references outside try/except
```

#### Acceptance Checklist
- [ ] Import guard is present (try/except)
- [ ] Code can import without Azure setup
- [ ] Mock returns valid token structure
- [ ] Token has both `token` and `expires_on` attributes
- [ ] No bare notebookutils references exist

---

### Task 1.2: Verify Azure AI Projects SDK Methods

#### What You're Checking
"Do all the SDK method calls actually exist in azure-ai-projects v1.0.0?"

#### Baby Steps to Verify Completion

**Step 1: Check Installed Package Version**
```powershell
pip show azure-ai-projects
```
**What to expect**: 
```
Name: azure-ai-projects
Version: 1.0.0  (or higher)
```

**Step 2: List All Method Calls in Code**
```powershell
# Find all method calls in fabric_ai_foundry_client.py
Select-String -Path fabric_ai_foundry_client.py -Pattern "client\.agents\." -AllMatches
```
**What to expect**: See these calls listed:
```
client.agents.get_agent(agent_id)
client.agents.create_thread()
client.agents.create_message(...)
client.agents.create_and_process_run(...)
client.agents.list_messages(...)
```

**Step 3: Verify Each Method in Documentation**

For EACH method, check the official docs:
1. Go to: https://github.com/Azure-Samples/ai-foundry-python-samples/tree/main/samples/agents
2. Search for method name in example files
3. Verify the signature matches your code

**Method Verification Table**:
```
[ ] get_agent(agent_id) - exists in examples?
[ ] create_thread() - exists in examples?
[ ] create_message(thread_id, role, content) - exists?
[ ] create_and_process_run(thread_id, assistant_id) - exists?
    ^ Or is it create_run() then process_run() separately?
[ ] list_messages(thread_id) - exists in examples?
```

**Step 4: Create Simple Test**
```python
# test_sdk_methods.py
from azure.ai.projects import AIProjectClient

# This will show what methods are available
client = AIProjectClient()  # Will fail if credentials missing, but that's OK
agents_methods = [m for m in dir(client.agents) if not m.startswith('_')]
print("Available agent methods:")
for method in sorted(agents_methods):
    print(f"  - {method}")

# Look for: create_and_process_run, create_thread, etc.
```

**Step 5: Update Code if Needed**
If method doesn't exist, update the call:
```python
# If create_and_process_run doesn't exist, use:
run = client.agents.create_run(thread_id, agent_id)
# Then poll for completion:
while run.status != "completed":
    run = client.agents.get_run(thread_id, run.id)
    time.sleep(1)
```

#### Acceptance Checklist
- [ ] azure-ai-projects version ≥ 1.0.0
- [ ] All method names exist in official examples
- [ ] No deprecated methods are used
- [ ] Code tested against real SDK (even if it fails due to auth)
- [ ] If method names incorrect, code is updated

---

### Task 1.3: Fix CSV Parsing

#### What You're Checking
"Does CSV parsing handle quoted fields, special characters, and different encodings?"

#### Baby Steps to Verify Completion

**Step 1: Verify Pandas is Installed**
```powershell
pip show pandas
```
**What to expect**: Version 2.0.0 or higher

**Step 2: Check Code Changes**
Open `agent_lakehouse_tools.py` and verify:
```
✓ Line with `import pandas as pd` exists
✓ read_csv_file() function uses `pd.read_csv()`
✓ NOT using naive `split(',')` anymore
✓ Returns first 100 rows using `.head(100)`
```

**Step 3: Test with Problematic CSVs**
Create `test_csv_parsing.py`:
```python
import io
import pandas as pd

# Test 1: Quoted fields
csv_with_quotes = '''name,description,price
Product A,"High quality, well made",19.99
Product B,"Includes ""special"" features",29.99'''

df = pd.read_csv(io.StringIO(csv_with_quotes))
print("Test 1 - Quoted fields:")
print(f"  Rows read: {len(df)}")
print(f"  Correct parse: {df.iloc[0]['description'] == 'High quality, well made'}")
assert len(df) == 2, "Should read 2 rows"
assert df.iloc[0]['price'] == 19.99, "Should parse price"
print("  ✅ PASSED\n")

# Test 2: Special characters
csv_special = '''id,message
1,Hello\nWorld
2,Line1\tLine2'''

df = pd.read_csv(io.StringIO(csv_special))
print("Test 2 - Special characters:")
print(f"  Rows read: {len(df)}")
print(f"  ✅ PASSED\n")

# Test 3: Large CSV (100+ rows)
csv_large = "id,value\n"
for i in range(150):
    csv_large += f"{i},{i*100}\n"

df = pd.read_csv(io.StringIO(csv_large))
df_100 = df.head(100)
print("Test 3 - Pagination:")
print(f"  Total rows: {len(df)}")
print(f"  First 100 rows: {len(df_100)}")
assert len(df_100) == 100, "Should return max 100 rows"
print("  ✅ PASSED\n")

print("✅ ALL CSV PARSING TESTS PASSED!")
```

**Step 4: Run the Tests**
```powershell
cd c:\repo\agent-framework\.workings
python test_csv_parsing.py
```

**Expected output**:
```
Test 1 - Quoted fields:
  Rows read: 2
  Correct parse: True
  ✅ PASSED

Test 2 - Special characters:
  Rows read: 2
  ✅ PASSED

Test 3 - Pagination:
  Total rows: 150
  First 100 rows: 100
  ✅ PASSED

✅ ALL CSV PARSING TESTS PASSED!
```

#### Acceptance Checklist
- [ ] Pandas import is present
- [ ] CSV parsing uses `pd.read_csv()` not `split(',')`
- [ ] Quoted fields test passes
- [ ] Special characters test passes
- [ ] Large CSV pagination test passes (100 row limit)

---

### Task 1.4: Add Pagination to File Listing

#### What You're Checking
"Does file listing work with lakehouses that have thousands of files?"

#### Baby Steps to Verify Completion

**Step 1: Verify Code Has Pagination**
Open `agent_lakehouse_tools.py` and check `list_lakehouse_files()`:
```python
# Should have:
✓ for path in fs_client.get_paths(...):  # Azure SDK has continuation token support
✓ Limit to ~100 files per call
✓ Return continuation_token in response
✓ Accept continuation_token as parameter
```

**Step 2: Check Response Structure**
Response should be:
```json
{
  "success": true,
  "file_count": 100,
  "files": [
    {"name": "file1.csv", "size": 1024, "last_modified": "2025-10-18T10:30:00"},
    // ... 99 more files
  ],
  "continuation_token": "next_page_token_value_here"  // If more files exist
}
```

**Step 3: Test Pagination Logic**
Create `test_pagination.py`:
```python
# Test that pagination response is structured correctly
import json

test_response = {
    "success": True,
    "file_count": 100,
    "files": [
        {"name": f"file{i}.csv", "size": 100*i, "last_modified": "2025-10-18"}
        for i in range(100)
    ],
    "continuation_token": "token123"  # Only if there are more files
}

# Verify structure
assert test_response["file_count"] == 100, "Should have 100 files"
assert len(test_response["files"]) == 100, "Files array should have 100 items"
assert "continuation_token" in test_response, "Should have continuation_token"
print("✅ Pagination response structure correct")

# Simulate next page
next_response = {
    "success": True,
    "file_count": 50,  # Fewer files on last page
    "files": [
        {"name": f"file{i}.csv", "size": 100*i, "last_modified": "2025-10-18"}
        for i in range(50)
    ]
    # No continuation_token = end of list
}

assert "continuation_token" not in next_response, "Last page shouldn't have token"
print("✅ Last page (no continuation_token) correct")
```

**Step 4: Run the Test**
```powershell
python test_pagination.py
```

**Expected output**:
```
✅ Pagination response structure correct
✅ Last page (no continuation_token) correct
```

#### Acceptance Checklist
- [ ] Response includes `continuation_token` field
- [ ] Pagination returns max 100 files per call
- [ ] API accepts `continuation_token` parameter
- [ ] Last page has no `continuation_token`
- [ ] File listing works with 1000+ file lakehouses

---

## PHASE 2: Testing Framework ✅

### Task 2.1: Create Test Configuration

#### What You're Checking
"Can I run tests WITHOUT Azure credentials?"

#### Baby Steps to Verify Completion

**Step 1: Check Pytest Install**
```powershell
pip show pytest pytest-asyncio
```

**Step 2: Verify conftest.py Exists**
```powershell
Test-Path tests/conftest.py
```

**Step 3: Run Pytest Collection**
```powershell
cd c:\repo\agent-framework\.workings
pytest tests/ --collect-only
```

**Expected output**: Should show all tests without errors:
```
<Module test_agent_tools.py>
  <Function test_list_lakehouse_files>
  <Function test_read_csv_file_with_quoted_fields>
  <Function test_get_lakehouse_info>
...
======== X tests collected ========
```

**Step 4: Verify Fixtures Available**
```powershell
pytest tests/conftest.py --collect-only
```

**Expected**: Should show fixtures:
```
fixtures defined from tests/conftest.py::mock_lakehouse_client
fixtures defined from tests/conftest.py::test_workspace_id
fixtures defined from tests/conftest.py::test_lakehouse_id
```

#### Acceptance Checklist
- [ ] conftest.py exists in tests/ folder
- [ ] Pytest collection shows no errors
- [ ] All fixtures listed correctly
- [ ] Fixtures use @pytest.fixture decorator
- [ ] No Azure credentials needed in conftest

---

### Task 2.2: Create Agent Tool Tests

#### What You're Checking
"Do all 4+ tool tests pass?"

#### Baby Steps to Verify Completion

**Step 1: Check Test File Exists**
```powershell
Test-Path tests/test_agent_tools.py
```

**Step 2: Run Tests and Count Passes**
```powershell
cd c:\repo\agent-framework\.workings
pytest tests/test_agent_tools.py -v
```

**Expected output**: Should show at least 4 tests passing:
```
tests/test_agent_tools.py::test_list_lakehouse_files PASSED       [ 25%]
tests/test_agent_tools.py::test_read_csv_file_with_quoted_fields PASSED [ 50%]
tests/test_agent_tools.py::test_read_csv_file_pagination PASSED   [ 75%]
tests/test_agent_tools.py::test_get_lakehouse_info PASSED         [100%]

======== 4 passed in 0.42s ========
```

**Step 3: Check Test Coverage**
```powershell
pytest tests/test_agent_tools.py --cov=agent_lakehouse_tools --cov-report=term-missing
```

**Expected**: Should cover main functions:
```
agent_lakehouse_tools.py:
  list_lakehouse_files          87%
  read_csv_file                 92%
  get_lakehouse_info            95%

TOTAL                           91%
```

**Step 4: Verify Each Test Function**
Open `tests/test_agent_tools.py` and confirm:
```
✓ test_list_lakehouse_files() - exists and has assertions
✓ test_read_csv_file_with_quoted_fields() - exists and has assertions
✓ test_read_csv_file_pagination() - exists and has assertions
✓ test_get_lakehouse_info() - exists and has assertions
```

#### Acceptance Checklist
- [ ] 4+ tests in test_agent_tools.py
- [ ] All tests marked with @pytest.mark.asyncio
- [ ] All tests pass (PASSED status)
- [ ] Code coverage > 85%
- [ ] Each test has clear assertions

---

### Task 2.3: Create Fabric Notebook Test

#### What You're Checking
"Can I test the Fabric client without being in a Fabric notebook?"

#### Baby Steps to Verify Completion

**Step 1: Check Test File Exists**
```powershell
Test-Path tests/test_fabric_client.py
```

**Step 2: Run Fabric Tests**
```powershell
cd c:\repo\agent-framework\.workings
pytest tests/test_fabric_client.py -v
```

**Expected output**:
```
tests/test_fabric_client.py::test_fabric_ml_credential_mock PASSED    [ 50%]
tests/test_fabric_client.py::test_connect_to_ai_foundry_mock PASSED   [100%]

======== 2 passed in 0.35s ========
```

**Step 3: Verify Mock Setup**
Open `tests/test_fabric_client.py` and look for:
```python
✓ @patch decorator for AIProjectClient
✓ MockedAIProjectClient setup
✓ test_fabric_ml_credential_mock() function
✓ test_connect_to_ai_foundry_mock() function
```

**Step 4: Check Token Mock**
Verify token mock has required attributes:
```python
# Should return object with these attributes:
mock_token.token = "mock-token-string"
mock_token.expires_on = 1729280400  # Unix timestamp
```

#### Acceptance Checklist
- [ ] test_fabric_client.py exists
- [ ] 2+ tests present
- [ ] Tests use @patch for Azure mocks
- [ ] All tests pass without Azure auth
- [ ] Mock token has token and expires_on attributes

---

### Task 2.4: Create Azure Function Tests

#### What You're Checking
"Do all Azure Function endpoints return correct responses?"

#### Baby Steps to Verify Completion

**Step 1: Check Test File Exists**
```powershell
Test-Path tests/test_function_app.py
```

**Step 2: Run Function Tests**
```powershell
cd c:\repo\agent-framework\.workings
pytest tests/test_function_app.py -v
```

**Expected output**: 3+ endpoint tests passing:
```
tests/test_function_app.py::test_list_files_endpoint PASSED        [ 33%]
tests/test_function_app.py::test_read_csv_endpoint PASSED          [ 66%]
tests/test_function_app.py::test_invalid_request PASSED            [100%]

======== 3 passed in 0.18s ========
```

**Step 3: Test Each Endpoint Manually**
```python
# test_endpoints.py
import requests
import json

BASE_URL = "http://localhost:7071/api"  # Local Azure Functions emulator

# Test 1: List Files
response = requests.post(
    f"{BASE_URL}/listFiles",
    json={
        "workspace_id": "test-workspace",
        "lakehouse_id": "test-lakehouse"
    }
)
print(f"Test 1 - List Files: {response.status_code}")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
data = response.json()
assert data["success"] == True, "Response should have success=true"
assert "file_count" in data, "Should have file_count"
print("  ✅ PASSED\n")

# Test 2: Read CSV
response = requests.post(
    f"{BASE_URL}/readCSVFile",
    json={
        "workspace_id": "test-workspace",
        "lakehouse_id": "test-lakehouse",
        "file_path": "data/test.csv"
    }
)
print(f"Test 2 - Read CSV: {response.status_code}")
assert response.status_code == 200
data = response.json()
assert "headers" in data, "Should have headers"
assert "data" in data, "Should have data"
print("  ✅ PASSED\n")

# Test 3: Bad Request
response = requests.post(
    f"{BASE_URL}/listFiles",
    json={}  # Missing required fields
)
print(f"Test 3 - Bad Request: {response.status_code}")
assert response.status_code == 400, f"Expected 400, got {response.status_code}"
print("  ✅ PASSED\n")

print("✅ ALL ENDPOINT TESTS PASSED!")
```

**Step 4: Check Response Formats**
For each endpoint, verify response:
```
✓ /listFiles returns: {success, file_count, files: [{name, size, last_modified}]}
✓ /readCSVFile returns: {success, row_count, headers, data}
✓ /getLakehouseInfo returns: {success, workspace_id, lakehouse_id, last_modified}
✓ Invalid requests return: 400 with error message
```

#### Acceptance Checklist
- [ ] test_function_app.py exists
- [ ] 3+ endpoint tests present
- [ ] All tests pass
- [ ] Response formats match spec
- [ ] Error handling tested (400 Bad Request)

---

## PHASE 3: Agent Testing Instructions ✅

### Task 3.1: Agent System Prompt with Testing Instructions

#### What You're Checking
"Can I follow the 4-part testing workflow with the agent?"

#### Baby Steps to Verify Completion

**Step 1: Find Agent Configuration**
In Azure AI Foundry:
1. Go to: https://ai.azure.com
2. Navigate to your Project
3. Click on Agent
4. Check "System prompt" tab

**Step 2: Verify Testing Instructions Exist**
System prompt should include:
```
✓ "## YOUR CAPABILITIES" section listing 3 tools
✓ "## TESTING INSTRUCTIONS" section
✓ "### Test 1: Basic Connection Test" pattern
✓ "### Test 2: File Discovery Test" pattern
✓ "### Test 3: Data Reading Test" pattern
✓ "### Test 4: Data Analysis Test" pattern
✓ "## CONVERSATION PATTERNS" section
✓ "## IMPORTANT CONSTRAINTS" section
```

**Step 3: Test Each Pattern**
Run these tests in order:

**Test 1: Basic Connection**
- User message: "Test if you can access the lakehouse"
- Expected agent response should:
  - Call `getLakehouseInfo` tool
  - Report "Successfully connected"
  - Include "last updated" timestamp

**Test 2: File Discovery**
- User message: "List all files in the lakehouse"
- Expected agent response should:
  - Call `listFiles` tool
  - Report file count
  - List CSV file names

**Test 3: Data Reading**
- User message: "Show me a sample of [filename]"
- Expected agent response should:
  - Call `readCSVFile` tool
  - Report row count
  - Show column headers
  - Display first 5 rows

**Test 4: Data Analysis**
- User message: "Analyze the data in [filename]"
- Expected agent response should:
  - Call `readCSVFile` tool
  - Provide statistics (min, max, counts)
  - Identify patterns

#### Acceptance Checklist
- [ ] System prompt is > 500 characters
- [ ] All 4 test patterns documented
- [ ] Each pattern has step-by-step workflow
- [ ] Constraints section is clear
- [ ] Conversation patterns are realistic

---

### Task 3.2: Sample Test Notebooks

#### What You're Checking
"Do all 4 sample test notebooks exist and run without errors?"

#### Baby Steps to Verify Completion

**Step 1: Check Files Exist**
```powershell
Test-Path samples/1_basic_connection_test.py
Test-Path samples/2_file_discovery_test.py
Test-Path samples/3_csv_read_test.py
Test-Path samples/4_analysis_test.py
```

**Step 2: Verify Each Has Required Structure**
For each file, check it contains:
```python
✓ Module docstring explaining test
✓ async def test_xxx() function
✓ Configuration section (ENDPOINT, AGENT_ID)
✓ Print statements with checkmarks (✓) and ✅
✓ Return True/False for pass/fail
✓ if __name__ == "__main__": block
```

**Step 3: Run Each Sample**
```powershell
# This will fail due to missing config, but should not crash
cd c:\repo\agent-framework\.workings
python samples/1_basic_connection_test.py
```

**Expected output**: Should show usage info, not crash:
```
============================================================
TEST 1: BASIC CONNECTION TEST
============================================================
[ERROR] ENDPOINT environment variable not set
Please set ENDPOINT and AGENT_ID in your environment
```

**Step 4: Check Content Quality**
Open each file and verify:
- [ ] `1_basic_connection_test.py` - Tests connection, agent responds
- [ ] `2_file_discovery_test.py` - Tests file listing
- [ ] `3_csv_read_test.py` - Tests CSV reading with error handling
- [ ] `4_analysis_test.py` - Tests analysis workflow

#### Acceptance Checklist
- [ ] All 4 sample files exist in samples/
- [ ] Each has clear docstring
- [ ] Each has async test function
- [ ] Each has configuration section
- [ ] Each has clear pass/fail output
- [ ] Each can be run independently

---

### Task 3.3: Create Local Testing Harness

#### What You're Checking
"Can I test agent logic WITHOUT deploying to Azure?"

#### Baby Steps to Verify Completion

**Step 1: Check File Exists**
```powershell
Test-Path tests/local_test_harness.py
```

**Step 2: Import and Test Harness**
```python
# test_harness_usage.py
from tests.local_test_harness import LocalLakehouseSimulator

# Create simulator
sim = LocalLakehouseSimulator()

# Test 1: List files
files_response = sim.list_files()
print(f"Test 1: {files_response}")
assert '"success": true' in files_response
assert '"file_count"' in files_response
print("✅ PASSED\n")

# Test 2: Read file
read_response = sim.read_file("sales.csv")
print(f"Test 2: {read_response}")
assert '"success": true' in read_response
print("✅ PASSED\n")

# Test 3: Not found
not_found = sim.read_file("nonexistent.csv")
print(f"Test 3: {not_found}")
assert '"success": false' in not_found
print("✅ PASSED\n")

print("✅ ALL HARNESS TESTS PASSED!")
```

**Step 3: Run Harness Tests**
```powershell
cd c:\repo\agent-framework\.workings
python test_harness_usage.py
```

**Expected output**:
```
Test 1: {"success": true, "file_count": 3, ...}
✅ PASSED

Test 2: {"success": true, "row_count": 2, ...}
✅ PASSED

Test 3: {"success": false, "error": "File not found"}
✅ PASSED

✅ ALL HARNESS TESTS PASSED!
```

**Step 4: Verify Harness Features**
Check `tests/local_test_harness.py` contains:
```python
✓ LocalLakehouseSimulator class
✓ list_files() method
✓ read_file() method
✓ get_info() method
✓ Pre-populated sample CSV files
✓ JSON response formatting
```

#### Acceptance Checklist
- [ ] local_test_harness.py exists
- [ ] LocalLakehouseSimulator class works
- [ ] list_files() returns proper JSON
- [ ] read_file() returns proper JSON
- [ ] Can test agent logic locally (no Azure needed)

---

## PHASE 4: Code Quality ✅

### Task 4.1: Replace Duck-Typed Token

#### What You're Checking
"Is the token object properly structured with dataclass?"

#### Baby Steps to Verify Completion

**Step 1: Check Import**
Open `fabric_ai_foundry_client.py` and verify:
```python
✓ from dataclasses import dataclass exists
```

**Step 2: Check Token Class**
Verify token class definition:
```python
✓ @dataclass decorator is present
✓ class Token: exists
✓ token: str attribute
✓ expires_on: int attribute
```

**Step 3: Test Token Creation**
```python
from fabric_ai_foundry_client import Token

# Create token
token = Token(token="test-token", expires_on=1729280400)

# Verify attributes
assert token.token == "test-token"
assert token.expires_on == 1729280400
print("✅ Token dataclass works correctly")
```

#### Acceptance Checklist
- [ ] Token class is a @dataclass
- [ ] Token has `token: str` attribute
- [ ] Token has `expires_on: int` attribute
- [ ] Token creation is simple and clear

---

### Task 4.2-4.4: Code Quality Items

#### What You're Checking
"Is code production-ready with logging, env validation, and cleanup?"

#### Baby Steps to Verify Completion

**Step 1: Check Logging**
```powershell
Select-String -Path agent_lakehouse_tools.py -Pattern "logger|logging"
```
Should find:
- [ ] import logging
- [ ] logger = logging.getLogger(__name__)
- [ ] logger.debug() calls
- [ ] logger.error() calls

**Step 2: Check Environment Validation**
```powershell
Select-String -Path function_app.py -Pattern "environ|getenv|KeyError"
```
Should find:
- [ ] Environment variable checks
- [ ] Clear error messages if missing
- [ ] No secrets hardcoded

**Step 3: Check Dependencies Cleanup**
```python
# Verify requirements.txt
import sys
sys.path.insert(0, 'c:\\repo\\agent-framework\\.workings')

with open('requirements.txt', 'r') as f:
    reqs = f.read()
    
# Should have:
assert 'azure-ai-projects' in reqs
assert 'azure-identity' in reqs
assert 'azure-storage-file-datalake' in reqs
assert 'pandas' in reqs

# Should NOT have:
# csv23 (if unused)

print("✅ Dependencies verified")
```

#### Acceptance Checklist
- [ ] Logging configured in agent_lakehouse_tools.py
- [ ] Logging configured in function_app.py
- [ ] Environment variables validated with helpful errors
- [ ] No hardcoded secrets
- [ ] Unused dependencies removed

---

## PHASE 5: Documentation ✅

### Task 5.1-5.3: Documentation Complete

#### What You're Checking
"Are deployment guide, testing guide, and architecture docs complete?"

#### Baby Steps to Verify Completion

**Step 1: Check Files Exist**
```powershell
Test-Path docs/DEPLOYMENT_GUIDE.md
Test-Path docs/TESTING_GUIDE.md
Test-Path docs/ARCHITECTURE.md
```

**Step 2: Verify Content**
For each doc, check it has:

**DEPLOYMENT_GUIDE.md**:
- [ ] Prerequisites section
- [ ] Step-by-step deployment instructions
- [ ] Configuration section
- [ ] Verification section
- [ ] Troubleshooting section

**TESTING_GUIDE.md**:
- [ ] How to run pytest
- [ ] How to run sample notebooks
- [ ] Local testing harness usage
- [ ] Integration testing steps
- [ ] Success criteria

**ARCHITECTURE.md**:
- [ ] 3-layer architecture diagram (or description)
- [ ] Component descriptions
- [ ] Data flow explanation
- [ ] Authentication flows
- [ ] Error handling approach

**Step 3: Check Completeness**
```powershell
$files = @(
    'docs/DEPLOYMENT_GUIDE.md',
    'docs/TESTING_GUIDE.md',
    'docs/ARCHITECTURE.md'
)

foreach ($file in $files) {
    $size = (Get-Item $file -ErrorAction SilentlyContinue).Length
    $lines = (Get-Content $file -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
    Write-Host "$file : $lines lines, $($size)b bytes"
}
```

Should show each document is > 500 lines

#### Acceptance Checklist
- [ ] DEPLOYMENT_GUIDE.md > 20 sections
- [ ] TESTING_GUIDE.md > 10 sections
- [ ] ARCHITECTURE.md includes all 3 layers
- [ ] All docs have code examples
- [ ] All docs have success criteria

---

## 🎓 Full Completion Checklist

### PHASE 1: Critical Fixes
- [ ] Task 1.1: Notebookutils import guard ✓
- [ ] Task 1.2: SDK methods verified ✓
- [ ] Task 1.3: CSV parsing with pandas ✓
- [ ] Task 1.4: Pagination implemented ✓

### PHASE 2: Testing Framework
- [ ] Task 2.1: conftest.py with fixtures ✓
- [ ] Task 2.2: 4+ agent tool tests ✓
- [ ] Task 2.3: Fabric client tests ✓
- [ ] Task 2.4: Azure Function tests ✓

### PHASE 3: Agent Testing
- [ ] Task 3.1: System prompt with 4 test patterns ✓
- [ ] Task 3.2: 4 sample test notebooks ✓
- [ ] Task 3.3: Local testing harness ✓

### PHASE 4: Code Quality
- [ ] Task 4.1: Token as dataclass ✓
- [ ] Task 4.2: Comprehensive logging ✓
- [ ] Task 4.3: Environment validation ✓
- [ ] Task 4.4: Dependency cleanup ✓

### PHASE 5: Documentation
- [ ] Task 5.1: Deployment guide ✓
- [ ] Task 5.2: Testing guide ✓
- [ ] Task 5.3: Architecture guide ✓

---

## ✅ Final Verification Command

Run this after everything is done:

```powershell
# Run all tests
pytest tests/ -v --cov=agent_lakehouse_tools --cov-report=term-missing

# Expected output should show:
# ✓ test_agent_tools.py - 4+ passing
# ✓ test_fabric_client.py - 2+ passing
# ✓ test_function_app.py - 3+ passing
# ✓ Code coverage > 85%
```

**If ALL tests pass with > 85% coverage: ✅ PROJECT COMPLETE!**

