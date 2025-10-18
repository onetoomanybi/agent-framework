# How to Add Lakehouse Path to Test Queries

## What is a Lakehouse Path?

A Fabric lakehouse path is the unique address to your lakehouse in Microsoft Fabric. It follows this format:

```text
abfss://[workspace_name]@[tenant]/[lakehouse_name].Lakehouse/Files
```

### Example

```text
abfss://WillowbrookWorkspace@mycompany/WillowbrookLakehouse.Lakehouse/Files
```

## How to Find Your Lakehouse Path

### Option 1: From Fabric UI

1. Go to your **Microsoft Fabric workspace**
2. Navigate to your **Lakehouse**
3. Click the **⋮ (More options)** button
4. Select **Properties**
5. Look for **ABFSS Path** - copy this value

### Option 2: From Lakehouse SQL Endpoint

1. In your Lakehouse, click **SQL Endpoint**
2. Look at the connection details
3. Extract the path from the connection string

## How to Add It to Test Queries

### Method 1: Update the Test Script (Recommended)

Edit `phase5_test_with_lakehouse_path.py` and replace:

```python
SAMPLE_LAKEHOUSE_PATH = "abfss://WillowbrookWorkspace@mycompany/WillowbrookLakehouse.Lakehouse/Files"
```

With your actual lakehouse path:

```python
SAMPLE_LAKEHOUSE_PATH = "abfss://your_workspace@your_tenant/your_lakehouse.Lakehouse/Files"
```

Then run:

```powershell
python willowbrook/src/phase5_test_with_lakehouse_path.py
```

### Method 2: Manual Query

When testing manually, include the lakehouse path in your prompt:

**Without path (agent asks for it):**

```text
"List the files in my lakehouse"
```

**With path (agent can execute):**

```text
"List the files in my lakehouse at abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files"
```

## Testing the Tools

Once you add the lakehouse path, the agent should:

1. ✅ Recognize the query
2. ✅ Understand it needs to call a tool
3. ✅ Extract the lakehouse path parameter
4. ✅ Call the appropriate tool (list_lakehouse_files, get_lakehouse_info, or read_csv_file)
5. ✅ Return results from your Fabric lakehouse

## Example Queries with Lakehouse Path

```python
# List files in lakehouse
"List all files in abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files"

# Get metadata
"What's the total size and file count of abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files?"

# Read CSV file
"Can you read the file data.csv from abfss://MyWorkspace@mytenant/MyLakehouse.Lakehouse/Files?"
```

## Troubleshooting

### Agent still asks for lakehouse path

Make sure the path is included in the query text exactly.

### Path format is wrong

Double-check the format: `abfss://[workspace]@[tenant]/[lakehouse].Lakehouse/Files`
No spaces allowed, case-sensitive for some parts.

### Can't find my lakehouse path

In Fabric UI → Lakehouse → Properties → Look for "ABFSS Path"

## Three Tool Functions Available

Once you add the lakehouse path, the agent can call:

1. **list_lakehouse_files** - Lists all files with sizes
2. **get_lakehouse_info** - Gets total file count and storage size
3. **read_csv_file** - Reads CSV files and returns data

All three functions require the `lakehouse_path` parameter in ABFSS format.
