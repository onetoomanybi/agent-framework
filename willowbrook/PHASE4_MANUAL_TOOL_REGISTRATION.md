# Phase 4: Manual Tool Registration in AI Foundry

Since tool registration varies by AI Foundry version, this guide provides the direct JSON schemas you can copy/paste into your agent.

---

## Quick Start: Copy These Tool Definitions

Go to **AI Foundry Portal** → **Your Agent** → **Add Tools**, then paste each function below:

---

## Tool 1: list_lakehouse_files

### Function Code
```python
def list_lakehouse_files(lakehouse_path: str = "lakehouse", 
                        path: str = "/Files", 
                        file_extension: str = None) -> str:
    """
    List files in the Fabric lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: 'lakehouse')
        path: Sub-path within lakehouse (default: '/Files')
        file_extension: Filter by extension, e.g., '.csv' (optional)
    
    Returns:
        JSON string with files, count, and sizes
    """
    import json
    from mssparkutils.fs import ls
    
    try:
        full_path = f"lakehouse://{lakehouse_path}{path}"
        items = ls(full_path)
        
        files = []
        for item in items:
            if file_extension is None or item.name.endswith(file_extension):
                files.append({
                    "name": item.name,
                    "size_bytes": item.size
                })
        
        return json.dumps({
            "success": True,
            "data": {
                "file_count": len(files),
                "files": files
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
```

### Parameter Schema
```json
{
  "type": "object",
  "properties": {
    "lakehouse_path": {
      "type": "string",
      "description": "Path to the lakehouse",
      "default": "lakehouse"
    },
    "path": {
      "type": "string",
      "description": "Sub-path within lakehouse",
      "default": "/Files"
    },
    "file_extension": {
      "type": "string",
      "description": "Filter by file extension (e.g., '.csv')",
      "default": null
    }
  },
  "required": []
}
```

---

## Tool 2: read_csv_file

### Function Code
```python
def read_csv_file(lakehouse_path: str = "lakehouse",
                 file_path: str = "/Files/sample.csv",
                 max_rows: int = 100) -> str:
    """
    Read CSV file from the lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: 'lakehouse')
        file_path: Path to CSV file within lakehouse
        max_rows: Maximum rows to return (default: 100)
    
    Returns:
        JSON string with column names, data, and row count
    """
    import json
    from pyspark.sql import SparkSession
    
    try:
        spark = SparkSession.builder.appName("ReadCSV").getOrCreate()
        
        full_path = f"abfss://{lakehouse_path}@*.dfs.core.windows.net{file_path}"
        df = spark.read.csv(full_path, header=True, inferSchema=True)
        
        data_rows = df.limit(max_rows).toPandas().to_dict('records')
        
        return json.dumps({
            "success": True,
            "data": {
                "columns": df.columns,
                "rows": data_rows,
                "row_count": len(data_rows),
                "total_rows": df.count()
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
```

### Parameter Schema
```json
{
  "type": "object",
  "properties": {
    "lakehouse_path": {
      "type": "string",
      "description": "Path to the lakehouse",
      "default": "lakehouse"
    },
    "file_path": {
      "type": "string",
      "description": "Path to CSV file within lakehouse",
      "default": "/Files/sample.csv"
    },
    "max_rows": {
      "type": "integer",
      "description": "Maximum rows to return",
      "default": 100
    }
  },
  "required": []
}
```

---

## Tool 3: get_lakehouse_info

### Function Code
```python
def get_lakehouse_info(lakehouse_path: str = "lakehouse") -> str:
    """
    Get metadata about the Fabric lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: 'lakehouse')
    
    Returns:
        JSON string with file count, folder count, and total size
    """
    import json
    from mssparkutils.fs import ls
    
    try:
        full_path = f"lakehouse://{lakehouse_path}/Files"
        items = ls(full_path)
        
        file_count = 0
        folder_count = 0
        total_size = 0
        
        for item in items:
            if item.name.endswith("/"):
                folder_count += 1
            else:
                file_count += 1
                total_size += item.size
        
        return json.dumps({
            "success": True,
            "data": {
                "file_count": file_count,
                "folder_count": folder_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
```

### Parameter Schema
```json
{
  "type": "object",
  "properties": {
    "lakehouse_path": {
      "type": "string",
      "description": "Path to the lakehouse",
      "default": "lakehouse"
    }
  },
  "required": []
}
```

---

## How to Register in AI Foundry

### Via UI (Manual)

1. Go to [ai.azure.com](https://ai.azure.com)
2. Select your **project**
3. Navigate to **Agents**
4. Click on **WillowbrookAgent**
5. Click **Add Tool** or **Tools** section
6. For each tool:
   - Select **Python Function** or **Custom Function**
   - Paste the **Function Code** from above
   - Paste the **Parameter Schema** as JSON
   - Click **Save**

### Via API (Programmatic)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

# Initialize client
credential = DefaultAzureCredential()
client = AIProjectClient.from_connection_string(
    conn_str="endpoint=YOUR_ENDPOINT",
    credential=credential
)

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_lakehouse_files",
            "description": "List files in the Fabric lakehouse",
            "parameters": {...}  # Use schema above
        }
    },
    # ... repeat for other 2 tools
]

# Register tools with agent
agent_id = "your_agent_id"
# Note: API method depends on your SDK version
```

---

## Verification Checklist

After registration, verify in AI Foundry:

- [ ] Agent "WillowbrookAgent" exists
- [ ] Tool 1: `list_lakehouse_files` is registered
- [ ] Tool 2: `read_csv_file` is registered
- [ ] Tool 3: `get_lakehouse_info` is registered
- [ ] All tools show correct parameters
- [ ] All tools show correct descriptions

---

## Troubleshooting

### Tool Not Appearing
- Check agent name spelling
- Verify you're in the correct project
- Try refreshing the page

### Parameter Errors
- Ensure JSON is valid (use jsonlint.com)
- Check all required fields are present
- Verify parameter types (string, integer, etc.)

### Execution Errors
- Verify Fabric notebook cell is running (all functions defined)
- Check file paths are correct
- Ensure files exist in the lakehouse

---

## Next: Phase 5

Once all 3 tools are registered and visible, you're ready for:

**Phase 5: Test Agent-Tool Integration**
- Open agent chat
- Ask: "List the files in my lakehouse"
- Agent should call `list_lakehouse_files`
- Verify response

See `PHASE5_TEST_INTEGRATION.md` for full Phase 5 steps.
