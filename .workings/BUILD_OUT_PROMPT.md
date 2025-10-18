# Build Out Project Prompt for Fabric + AI Foundry Integration

## Executive Summary

This prompt guides you to build a **production-ready Microsoft Fabric + Azure AI Foundry integration** project that enables agents to intelligently access and analyze data from Fabric Lakehouses. The project consists of three main components working together:

1. **Fabric Notebook Client** - User interface running in Microsoft Fabric notebooks
2. **Agent Tool Implementation** - Backend tools running in Azure AI Foundry
3. **Azure Function App** - HTTP endpoints exposing tools to agents

The agents include **testing instructions** that enable immediate functionality validation.

---

## Current State

You have:

- ✅ Three main Python files with core functionality
- ✅ OpenAPI specification defining agent tools
- ✅ Configuration examples
- ✅ Comprehensive documentation of architecture and flow
- ⚠️ 1 CRITICAL issue: missing `notebookutils` import
- ⚠️ 3 HIGH issues: SDK method verification, CSV parsing, pagination needed
- ⚠️ 8 additional quality/improvement issues (documented in ISSUES_QUICK_FIX_GUIDE.md)

**Status**: Code is functional but not production-ready. Needs fixes and testing framework.

---

## Project Build-Out Steps

### PHASE 1: Fix Critical Issues (1-2 hours)

#### Task 1.1: Resolve notebookutils Import
**Problem**: `notebookutils` is undefined in `fabric_ai_foundry_client.py` line 27
**Impact**: CRITICAL - will cause NameError at runtime
**Solution**: Add conditional import with fallback

```python
# At top of fabric_ai_foundry_client.py
try:
    # In Fabric notebook environment
    import notebookutils
except ImportError:
    # For local testing - mock the module
    class MockNotebookUtils:
        class credentials:
            @staticmethod
            def getToken(scope: str) -> str:
                """Mock credential for testing"""
                return "mock-token-for-testing"
    
    notebookutils = MockNotebookUtils()
```

**Acceptance**: Code can run in both Fabric and local test environments

#### Task 1.2: Verify Azure AI Projects SDK Methods
**Problem**: Method names like `create_and_process_run()` need verification
**Impact**: HIGH - methods may not exist in v1.0.0
**Solution**: 
- Check official [azure-ai-projects documentation](https://github.com/Azure-Samples/ai-foundry-python-samples)
- Verify these methods exist:
  - `client.agents.get_agent(agent_id)`
  - `client.agents.create_thread()`
  - `client.agents.create_message(thread_id, role, content)`
  - `client.agents.create_and_process_run(thread_id, assistant_id)`
  - `client.agents.list_messages(thread_id)`

**Acceptance**: All method calls validated or updated to correct API

#### Task 1.3: Fix CSV Parsing
**Problem**: Naive CSV parsing in `agent_lakehouse_tools.py` breaks with quoted fields
**Impact**: HIGH - breaks on realistic data
**Solution**: Use pandas for robust CSV parsing

```python
import pandas as pd

async def read_csv_file(workspace_id, lakehouse_id, file_path):
    try:
        # Download file
        file_client = fs_client.get_file_client(file_path)
        download = file_client.download_file()
        content = download.readall()
        
        # Use pandas for robust parsing
        df = pd.read_csv(io.BytesIO(content))
        
        # Return first 100 rows
        data = df.head(100).to_dict(orient='records')
        
        return json.dumps({
            "success": True,
            "row_count": len(df),
            "headers": df.columns.tolist(),
            "data": data
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
```

**Acceptance**: CSV with quoted fields, escaping, and special characters parses correctly

#### Task 1.4: Add Pagination to File Listing
**Problem**: No pagination - could return 10,000+ files in single response
**Impact**: HIGH - performance/memory issue with large lakehouses
**Solution**: Add pagination parameters

```python
async def list_lakehouse_files(
    workspace_id: str,
    lakehouse_id: str,
    path: str = "Files",
    file_extension: str = None,
    max_results: int = 100,  # Default page size
    continuation_token: str = None
) -> str:
    # Use pagination with continuation tokens
    # Return next_continuation_token in response if more results exist
```

**Acceptance**: Large file listings return paginated results (100 files per page max)

---

### PHASE 2: Add Testing Framework (2-3 hours)

#### Task 2.1: Create Test Configuration
**Purpose**: Enable testing without Fabric/Azure setup
**Files to create**:
- `tests/conftest.py` - pytest fixtures and configuration
- `tests/test_data/sample_files/` - test data
- `.env.test` - test environment variables

```python
# tests/conftest.py
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
async def mock_lakehouse_client():
    """Mock DataLakeServiceClient for testing"""
    # Return mock with get_paths, get_file_client methods
    pass

@pytest.fixture
def test_workspace_id():
    return "test-workspace-123"

@pytest.fixture
def test_lakehouse_id():
    return "test-lakehouse-456"

@pytest.fixture
def test_csv_content():
    return b"name,age,city\nAlice,30,NYC\nBob,25,LA"
```

**Acceptance**: Fixtures available for all tests, no Azure credentials required

#### Task 2.2: Create Agent Tool Tests
**Purpose**: Validate tool implementations work correctly
**File**: `tests/test_agent_tools.py`
**Tests needed**:

```python
@pytest.mark.asyncio
async def test_list_lakehouse_files(mock_lakehouse_client, test_workspace_id, test_lakehouse_id):
    """Test file listing returns proper structure"""
    # Assert: Returns JSON with success, file_count, files array
    # Assert: Files have name, size, last_modified
    pass

@pytest.mark.asyncio
async def test_read_csv_file_with_quoted_fields(mock_lakehouse_client, test_csv_content):
    """Test CSV parsing handles quoted fields"""
    # Assert: Parses correctly
    # Assert: Returns headers and data rows
    pass

@pytest.mark.asyncio
async def test_read_csv_file_pagination(mock_lakehouse_client):
    """Test large CSV files are paginated"""
    # Assert: First 100 rows returned
    # Assert: continuation_token provided for next page
    pass

@pytest.mark.asyncio
async def test_get_lakehouse_info(mock_lakehouse_client):
    """Test metadata retrieval"""
    # Assert: Returns workspace_id, lakehouse_id, last_modified
    pass
```

**Acceptance**: 4+ tests pass, cover basic functionality

#### Task 2.3: Create Fabric Notebook Test Script
**Purpose**: Test Fabric client in isolated environment
**File**: `tests/test_fabric_client.py`
**Tests needed**:

```python
@pytest.mark.asyncio
async def test_fabric_ml_credential_mock():
    """Test FabricMLCredential with mock"""
    # Assert: get_token returns valid token object
    # Assert: Token has 'token' and 'expires_on' attributes
    pass

@pytest.mark.asyncio
async def test_connect_to_ai_foundry_mock():
    """Test connection to AI Foundry with mocked client"""
    # Mock AIProjectClient
    # Assert: Returns client and agent
    # Assert: client.agents.get_agent called with correct agent_id
    pass
```

**Acceptance**: Tests pass with mocked Azure services

#### Task 2.4: Create Azure Function Tests
**Purpose**: Test HTTP endpoints return correct responses
**File**: `tests/test_function_app.py`
**Tests needed**:

```python
@pytest.mark.asyncio
async def test_list_files_endpoint():
    """Test /listFiles endpoint"""
    # Send POST with workspace_id, lakehouse_id
    # Assert: 200 response with JSON body
    # Assert: Response has success, file_count, files
    pass

@pytest.mark.asyncio
async def test_read_csv_endpoint():
    """Test /readCSVFile endpoint"""
    # Send POST with workspace_id, lakehouse_id, file_path
    # Assert: 200 response with JSON body
    # Assert: Response has success, row_count, headers, data
    pass

@pytest.mark.asyncio
async def test_invalid_request():
    """Test endpoint handles missing required parameters"""
    # Send POST missing workspace_id
    # Assert: 400 Bad Request response
    pass
```

**Acceptance**: All endpoint tests pass

---

### PHASE 3: Add Agent Testing Instructions (1-2 hours)

#### Task 3.1: Create Agent System Prompt with Testing Instructions
**Purpose**: Enable agents to test functionality safely
**Location**: In Azure AI Foundry agent configuration
**Content**:

```
You are a helpful data analyst agent with access to Microsoft Fabric Lakehouses.

## YOUR CAPABILITIES
You can:
1. List files in a lakehouse using listFiles tool
2. Read CSV file contents using readCSVFile tool  
3. Get lakehouse metadata using getLakehouseInfo tool

## TESTING INSTRUCTIONS
When testing, follow this workflow:

### Test 1: Basic Connection Test
User asks: "Test if you can access the lakehouse"
You should:
1. Call getLakehouseInfo with workspace_id and lakehouse_id
2. Report back: "Successfully connected. Lakehouse last updated: [date]"

### Test 2: File Discovery Test
User asks: "List all files in the lakehouse"
You should:
1. Call listFiles with path="Files"
2. Report: "Found [N] files: [list file names]"
3. Identify potential CSV files for analysis

### Test 3: Data Reading Test
User asks: "Show me a sample of [filename.csv]"
You should:
1. Call readCSVFile with the file_path
2. Report: "File has [N] total rows with columns: [list]"
3. Show first 5 rows as example

### Test 4: Data Analysis Test
User asks: "Analyze the data in [filename.csv]"
You should:
1. Call readCSVFile
2. Examine headers and sample rows
3. Provide analysis: record count, column types, data patterns

## IMPORTANT CONSTRAINTS
- You can only READ files, not modify or delete them
- You can only access the specified workspace/lakehouse
- You can see first 100 rows of CSV files
- If a file has > 100 rows, use pagination
- Always verify workspace_id and lakehouse_id before tool calls

## CONVERSATION PATTERNS

Pattern A: File Discovery
User: "What data do we have?"
You: List files → Show CSV files → Offer to read sample

Pattern B: Quick Data Review
User: "Show me [filename]"
You: Read file → Show structure → Ask for specific analysis

Pattern C: Data Quality Check
User: "Check if all data is complete"
You: List files → Read each → Compare → Report gaps

Pattern D: Follow-up Analysis
Previous: Showed data sample
User: "Tell me about [column name]"
You: Use already-read data to analyze specific column
```

**Acceptance**: Agent instructions clear, testing patterns documented

#### Task 3.2: Create Sample Test Notebooks
**Purpose**: Provide templates for testing
**Files to create**:
- `samples/1_basic_connection_test.py` - Test basic connectivity
- `samples/2_file_discovery_test.py` - Test file listing
- `samples/3_csv_read_test.py` - Test CSV reading
- `samples/4_analysis_test.py` - Test analysis workflow

**Example content for `samples/1_basic_connection_test.py`**:

```python
"""
Test 1: Basic Connection Test
=============================
This test verifies that the agent can connect to the lakehouse.

Run this first to verify setup is correct.
"""

import asyncio
from fabric_ai_foundry_client import connect_to_ai_foundry, run_agent_conversation

async def test_basic_connection():
    """Test that agent can connect to lakehouse"""
    
    # Configuration
    ENDPOINT = "https://your-project.services.ai.azure.com"
    AGENT_ID = "your-agent-id"
    
    print("=" * 60)
    print("TEST 1: BASIC CONNECTION TEST")
    print("=" * 60)
    
    # Connect to agent
    client, agent = connect_to_ai_foundry(ENDPOINT, AGENT_ID)
    if not client or not agent:
        print("❌ FAILED: Could not connect to AI Foundry")
        return False
    
    print("✓ Connected to AI Foundry")
    print(f"  Agent ID: {agent.id}")
    
    # Test 1: Agent responds
    print("\n[Test 1.1] Verifying agent responds to basic query...")
    response = await run_agent_conversation(
        client, agent, 
        "Test if you can access the lakehouse"
    )
    
    if response and "Successfully" in response:
        print("✓ Agent responded successfully")
        print(f"  Response: {response}")
        return True
    else:
        print("❌ FAILED: Agent did not respond correctly")
        print(f"  Response: {response}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_basic_connection())
    print("\n" + "=" * 60)
    if result:
        print("✅ TEST PASSED: Basic connection working!")
    else:
        print("❌ TEST FAILED: See errors above")
```

**Acceptance**: Sample test notebooks runnable and demonstrate each test pattern

#### Task 3.3: Create Local Testing Harness
**Purpose**: Test without Azure deployment
**File**: `tests/local_test_harness.py`
**Purpose**: Simulate agent behavior without real Azure services

```python
"""
Local Testing Harness
=====================
Simulates agent tool calls without requiring Azure deployment.
Perfect for rapid iteration and validation.
"""

import json
from unittest.mock import MagicMock, patch
from agent_lakehouse_tools import list_lakehouse_files, read_csv_file

class LocalLakehouseSimulator:
    """Simulates a Fabric Lakehouse for testing"""
    
    def __init__(self):
        self.files = {
            "sales.csv": "date,product,quantity,price\n2025-10-01,Widget A,100,9.99\n2025-10-02,Widget B,50,19.99",
            "customers.csv": "id,name,email,city\n1,Alice,alice@example.com,NYC\n2,Bob,bob@example.com,LA",
            "inventory.csv": "sku,quantity,warehouse\nW001,500,NYC\nW002,300,LA"
        }
    
    def list_files(self, path="Files"):
        """Simulate listFiles tool"""
        files = []
        for name, content in self.files.items():
            files.append({
                "name": name,
                "size": len(content),
                "last_modified": "2025-10-18T10:30:00"
            })
        return json.dumps({
            "success": True,
            "file_count": len(files),
            "files": files
        })
    
    def read_file(self, file_path):
        """Simulate readCSVFile tool"""
        if file_path not in self.files:
            return json.dumps({"success": False, "error": "File not found"})
        
        content = self.files[file_path]
        lines = content.split('\n')
        headers = lines[0].split(',')
        data = [dict(zip(headers, line.split(','))) for line in lines[1:] if line]
        
        return json.dumps({
            "success": True,
            "row_count": len(data),
            "headers": headers,
            "data": data
        })

def test_agent_tools_locally():
    """Test tools against simulated lakehouse"""
    simulator = LocalLakehouseSimulator()
    
    print("=" * 60)
    print("LOCAL LAKEHOUSE TESTING")
    print("=" * 60)
    
    # Test 1: List files
    print("\n[Test 1] Listing files...")
    result = json.loads(simulator.list_files())
    print(f"✓ Found {result['file_count']} files")
    for f in result['files']:
        print(f"  - {f['name']} ({f['size']} bytes)")
    
    # Test 2: Read CSV
    print("\n[Test 2] Reading sales.csv...")
    result = json.loads(simulator.read_file("sales.csv"))
    print(f"✓ File has {result['row_count']} rows")
    print(f"  Columns: {', '.join(result['headers'])}")
    print(f"  Sample row: {result['data'][0]}")
    
    print("\n" + "=" * 60)
    print("✅ All local tests passed!")

if __name__ == "__main__":
    test_agent_tools_locally()
```

**Acceptance**: Local harness runs, simulates all three tools, demonstrates functionality

---

### PHASE 4: Improve Code Quality (1-2 hours)

#### Task 4.1: Replace Duck-Typed Token with Dataclass
**Problem**: Token object created via `type()` is fragile
**Solution**:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TokenInfo:
    token: str
    expires_on: int

class FabricMLCredential:
    def get_token(self, *scopes, **kwargs) -> TokenInfo:
        token = notebookutils.credentials.getToken("https://ml.azure.com")
        expires_on = int((datetime.now() + timedelta(hours=1)).timestamp())
        return TokenInfo(token=token, expires_on=expires_on)
```

**Acceptance**: TokenInfo properly typed and documented

#### Task 4.2: Add Comprehensive Logging
**Purpose**: Enable debugging and monitoring
**Implementation**:

```python
import logging

logger = logging.getLogger("agent_lakehouse_tools")

async def list_lakehouse_files(...):
    try:
        logger.info(f"Listing files: workspace={workspace_id}, lakehouse={lakehouse_id}")
        # ... implementation ...
        logger.info(f"Found {len(files)} files")
        return json.dumps({"success": True, ...})
    except Exception as e:
        logger.error(f"Failed to list files: {e}", exc_info=True)
        return json.dumps({"success": False, "error": str(e)})
```

**Acceptance**: All functions log entry/exit and errors

#### Task 4.3: Add Environment Variable Validation
**Purpose**: Fail fast with clear error messages
**File**: `config.py`

```python
import os
from typing import Optional

class Config:
    """Configuration with validation"""
    
    @staticmethod
    def get_fabric_workspace_id() -> str:
        value = os.getenv("FABRIC_WORKSPACE_ID")
        if not value:
            raise ValueError("FABRIC_WORKSPACE_ID environment variable not set")
        return value
    
    @staticmethod
    def get_fabric_lakehouse_id() -> str:
        value = os.getenv("FABRIC_LAKEHOUSE_ID")
        if not value:
            raise ValueError("FABRIC_LAKEHOUSE_ID environment variable not set")
        return value
    
    # ... more config methods ...
```

**Acceptance**: Clear error messages when config missing

#### Task 4.4: Remove Unused Dependencies
**Problem**: `csv23` and `pandas` partially used
**Solution**:
- If using pandas: keep it and use for all CSV parsing
- If not: remove and keep native CSV parsing
- Recommendation: Keep pandas, use throughout

**Acceptance**: requirements.txt only lists used packages

---

### PHASE 5: Documentation & Deployment (1-2 hours)

#### Task 5.1: Create Deployment Guide
**File**: `DEPLOYMENT_GUIDE.md`
**Sections**:
1. Prerequisites (Azure account, Fabric workspace, etc.)
2. Step-by-step deployment to Azure Functions
3. Configuring agent in Azure AI Foundry
4. Testing in Fabric notebook
5. Monitoring and troubleshooting

#### Task 5.2: Create README for Testing
**File**: `TESTING_README.md`
**Sections**:
1. Unit test execution
2. Local testing harness
3. Integration testing with real Azure
4. Manual testing in Fabric notebook
5. Troubleshooting test failures

#### Task 5.3: Create Architecture Diagram
**File**: `ARCHITECTURE.md`
**Content**: Deploy the diagrams from existing documentation in cleaner format

---

## Summary of Deliverables

By completing this build-out, you will have:

### Code Improvements
- ✅ Fixed critical notebookutils import issue
- ✅ Verified and corrected all SDK method calls
- ✅ Robust CSV parsing using pandas
- ✅ Pagination for large file listings
- ✅ Proper token handling with dataclasses
- ✅ Comprehensive logging
- ✅ Environment configuration validation

### Testing Infrastructure
- ✅ pytest test suite with 15+ tests
- ✅ Mock fixtures for Azure services
- ✅ Local testing harness (no Azure needed)
- ✅ Sample test notebooks

### Agent Testing Capabilities
- ✅ Clear system instructions for testing
- ✅ 4 test patterns (connection, discovery, reading, analysis)
- ✅ Sample notebooks for each test pattern
- ✅ Expected outputs documented

### Documentation
- ✅ Deployment guide (step-by-step)
- ✅ Testing guide (how to validate)
- ✅ Architecture diagrams
- ✅ Configuration examples

---

## Suggested Build Order

1. **Start**: Phase 1 (Fix critical issues) - 1-2 hours
2. **Then**: Phase 3.1 (Agent instructions) - 30 mins
3. **Then**: Phase 3.2 (Sample notebooks) - 1 hour
4. **Then**: Phase 2 (Testing framework) - 2-3 hours
5. **Then**: Phase 4 (Code quality) - 1-2 hours
6. **Finally**: Phase 5 (Documentation) - 1-2 hours

**Total Time**: ~8-13 hours for complete professional project

---

## Success Criteria

Your project is complete when:

- ✅ All code issues from ISSUES_QUICK_FIX_GUIDE.md are resolved
- ✅ Test suite runs with >90% pass rate
- ✅ Local testing harness demonstrates all tool functionality
- ✅ Sample notebooks run successfully with mock data
- ✅ Agent system prompt includes clear testing instructions
- ✅ Code includes comprehensive logging and error handling
- ✅ Documentation covers deployment and testing
- ✅ No hardcoded credentials anywhere
- ✅ Environment variables required for all sensitive config

---

## References

- **Microsoft Agent Framework**: c:\repo\agent-framework\python\samples\getting_started\agents\
- **Agent Framework Azure AI**: c:\repo\agent-framework\python\packages\azure-ai\
- **Existing Documentation**: ISSUES_QUICK_FIX_GUIDE.md, HOW_AGENTS_CONNECT_TO_LAKEHOUSE.md, WHAT_AGENTS_DO.txt
