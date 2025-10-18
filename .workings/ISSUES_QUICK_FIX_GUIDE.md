# QUICK REFERENCE: Issues Found

## 🔴 CRITICAL (Will Crash)

### fabric_ai_foundry_client.py - Line 27

**Issue**: `notebookutils` is not imported

```python
# WRONG - This will crash
token = notebookutils.credentials.getToken("https://ml.azure.com")
# NameError: name 'notebookutils' is not defined
```

**Fix**: Add proper import guard

```python
try:
    from notebookutils.visualization import display
    FABRIC_ENVIRONMENT = True
except ImportError:
    FABRIC_ENVIRONMENT = False

def get_token(self, *scopes, **kwargs):
    if not FABRIC_ENVIRONMENT:
        raise RuntimeError("This only works in Fabric notebooks")
    token = notebookutils.credentials.getToken("https://ml.azure.com")
```

---

## 🟠 HIGH (Functional Issues)

### 1. agent_lakehouse_tools.py - CSV Parsing (Lines 165-170)

**Issue**: Naive CSV parsing breaks with quoted fields

```python
# WRONG - Doesn't handle: "Smith, John", Jr.
values = line.split(',')  # ❌ Breaks with quoted commas
```

**Fix**: Use pandas (already in requirements!)

```python
import pandas as pd

# GOOD - Handles all CSV edge cases
df = pd.read_csv(BytesIO(content))
rows = df.to_dict('records')
```

### 2. fabric_ai_foundry_client.py - Verify SDK Methods

**Issue**: Methods need verification against azure-ai-projects v1.0.0+

```python
# These need to be verified:
client.agents.create_and_process_run()  # ⚠️ Check if this exists
client.agents.get_agent()                # ⚠️ Check if this exists
```

**Action**: Check the actual SDK documentation or run tests

### 3. function_app.py - Missing Pagination

**Issue**: No limit on returned files

```python
# WRONG - Could return 10,000 files in response
files = []
for p in paths:
    files.append({...})
return json.dumps({"files": files})  # ❌ No pagination
```

**Fix**: Add limit and offset

```python
LIMIT = 100
offset = req_body.get('offset', 0)

files = files[offset:offset + LIMIT]
return json.dumps({
    "files": files,
    "total": total_count,
    "offset": offset,
    "limit": LIMIT
})
```

---

## 🟡 MEDIUM (Quality Issues)

### 1. Hardcoded UTF-8 Encoding

```python
# WRONG - Assumes UTF-8
text_content = content.decode('utf-8')  # ❌ What if file is latin-1?
```

**Fix**: Handle encoding gracefully

```python
try:
    text_content = content.decode('utf-8')
except UnicodeDecodeError:
    text_content = content.decode('latin-1')
```

### 2. Token Object Duck Typing

```python
# WRONG - Fragile duck typing
return type('TokenInfo', (), {
    'token': token,
    'expires_on': expires_on
})()
```

**Fix**: Use proper dataclass

```python
from dataclasses import dataclass

@dataclass
class TokenInfo:
    token: str
    expires_on: int
```

### 3. Unused Dependency

```
# requirements.txt
csv23>=0.3.3  # ❌ Listed but never imported
```

**Fix**: Remove csv23, use stdlib `csv` module

---

## Summary by File

### agent_lakehouse_tools.py: 2 🟠 HIGH, 2 🟡 MEDIUM

- ✅ Azure Storage API usage correct
- ❌ CSV parsing too simple
- ⚠️ No encoding handling
- ⚠️ Pandas unused

### fabric_ai_foundry_client.py: 1 🔴 CRITICAL, 2 🟠 HIGH, 2 🟡 MEDIUM

- 🔴 **notebookutils not imported** - WILL CRASH
- ❌ SDK methods not verified
- ⚠️ Token object poorly implemented
- ⚠️ No expiration handling

### function_app.py: 1 🟠 HIGH, 2 🟡 MEDIUM

- ✅ Azure Functions API usage correct
- ❌ No pagination
- ⚠️ No file size limits
- ⚠️ No rate limiting

---

## Test Each Issue

### Test 1: Can we import the modules?

```bash
python -c "import fabric_ai_foundry_client"
# Expected: ModuleNotFoundError (notebookutils) ⚠️ Or NameError
```

### Test 2: CSV parsing with complex data

```python
csv_data = '''name,address,age
"Smith, John",Jr.,"123 Main St, Apt 4",25'''
# Current code breaks ❌
# Fixed code handles it ✅
```

### Test 3: List files pagination

```python
# Request 100,000 files
response = await list_lakehouse_files(ws, lh, path)
# Current: Returns all files
# Fixed: Returns 100, provides pagination info
```

---

## Deployment Checklist

- [ ] Fix `notebookutils` import (CRITICAL)
- [ ] Verify SDK method names
- [ ] Replace CSV parsing with pandas
- [ ] Add pagination to list endpoint
- [ ] Add encoding error handling
- [ ] Add file size validation
- [ ] Test in Fabric notebook environment
- [ ] Test in Azure Function environment
- [ ] Run unit tests on each change
