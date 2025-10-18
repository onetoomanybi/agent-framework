# Phase 3: Test Cells 2 & 3

Copy and paste these into your Fabric notebook.

---

## Cell 2: Test get_lakehouse_info()

```python
# Test 2: Get lakehouse metadata
print("=" * 70)
print("TEST 2: Get lakehouse metadata")
print("=" * 70)

result2 = get_lakehouse_info()
print("Response:")
print(result2)

# Parse and display nicely
data2 = json.loads(result2)
if data2["success"]:
    print(f"\n✅ SUCCESS!")
    print(f"   Total files: {data2['data']['file_count']}")
    print(f"   Total folders: {data2['data']['folder_count']}")
    print(f"   Total size: {data2['data']['total_size_mb']} MB")
    print(f"   Total bytes: {data2['data']['total_size_bytes']:,}")
else:
    print(f"❌ ERROR: {data2['error']}")

print()
```

**Expected Output:**
```
======================================================================
TEST 2: Get lakehouse metadata
======================================================================
Response:
{"success": true, "data": {"file_count": 5, "folder_count": 2, "total_size_bytes": 51200, "total_size_mb": 0.05, "timestamp": "2025-10-18T20:30:45.123456"}, "error": null}

✅ SUCCESS!
   Total files: 5
   Total folders: 2
   Total size: 0.05 MB
   Total bytes: 51,200
```

---

## Cell 3: Test read_csv_file()

```python
# Test 3: Read CSV file from /Files folder
print("=" * 70)
print("TEST 3: Read CSV file from /Files folder")
print("=" * 70)

# Try to read a CSV from /Files
# Adjust the filename to match an actual CSV in your lakehouse
# Common names: sample.csv, data.csv, test.csv, sales.csv, etc.
result3 = read_csv_file(
    lakehouse_path="lakehouse",
    file_path="/Files/sample.csv",  # <-- CHANGE to your actual CSV filename
    max_rows=5
)

print("Response (first 800 chars):")
response_obj = json.loads(result3)
response_str = json.dumps(response_obj, indent=2)
print(response_str[:800])
if len(response_str) > 800:
    print("... (truncated)")

# Parse and display nicely
if response_obj["success"]:
    print(f"\n✅ SUCCESS!")
    print(f"   Columns: {response_obj['data']['columns']}")
    print(f"   Rows returned: {response_obj['data']['row_count']}")
    print(f"   Total rows in file: {response_obj['data']['total_rows']}")
    
    if response_obj['data']['rows']:
        print(f"\n   First row preview:")
        first_row = response_obj['data']['rows'][0]
        for i, (key, value) in enumerate(first_row.items()):
            if i < 3:  # Show first 3 columns
                print(f"     {key}: {value}")
        if len(first_row) > 3:
            print(f"     ... and {len(first_row) - 3} more columns")
else:
    print(f"❌ ERROR: {response_obj['error']}")
    print("\n   Troubleshooting:")
    print("   1. Make sure the file path is correct")
    print("   2. CSV file must be in /Files/ folder")
    print("   3. Try a different filename if sample.csv doesn't exist")
    print("   4. File must be readable CSV format")

print()
```

**Expected Output (if CSV exists):**
```
======================================================================
TEST 3: Read CSV file from /Files folder
======================================================================
Response (first 800 chars):
{
  "success": true,
  "data": {
    "rows": [
      {
        "id": "1",
        "name": "Alice",
        "amount": "100.50"
      },
      ...
    ],
    "columns": [
      "id",
      "name",
      "amount"
    ],
    "row_count": 5,
    "total_rows": 1000,
    "timestamp": "2025-10-18T20:31:12.654321"
  },
  "error": null
}

✅ SUCCESS!
   Columns: ['id', 'name', 'amount']
   Rows returned: 5
   Total rows in file: 1000

   First row preview:
     id: 1
     name: Alice
     amount: 100.50
```

---

## How to Find Your CSV Files

If you're not sure what CSV files exist, run this quick cell first:

```python
# List all CSV files in /Files
print("Finding CSV files in /Files...")
try:
    files = mssparkutils.fs.ls("lakehouse/Files")
    csv_files = [f for f in files if f.name.endswith('.csv')]
    
    if csv_files:
        print(f"\n✅ Found {len(csv_files)} CSV files:")
        for f in csv_files:
            print(f"   - {f.name} ({f.size:,} bytes)")
    else:
        print("\n❌ No CSV files found in /Files")
        print("\nAll files in /Files:")
        for f in files[:10]:
            print(f"   - {f.name}")
except Exception as e:
    print(f"❌ Error listing files: {e}")
```

---

## Success Criteria for Phase 3

✅ **Cell 2** runs without errors  
✅ **Cell 2** returns lakehouse metadata (file count, folder count, size)  
✅ **Cell 3** runs without errors  
✅ **Cell 3** returns CSV data with columns and rows  
✅ All responses are valid JSON with `"success": true`  

---

## Next: Phase 4

Once all tests pass, you're ready for **Phase 4: Create AI Foundry Agent**!

At that point, we'll:
1. Go to https://ai.azure.com
2. Create a new agent
3. Register these 3 functions as tools
4. Test the agent calling the tools
