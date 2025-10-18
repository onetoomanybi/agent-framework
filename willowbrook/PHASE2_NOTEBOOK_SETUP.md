# Phase 2: Fabric Notebook Setup - Complete Cell Guide

## Problem We're Solving

Fabric notebook cells can have isolated namespaces. The solution: **Put everything in ONE cell** and run it together.

---

## Solution: Single Cell Approach

### Delete All Previous Cells

Start fresh. Delete any cells you added before.

---

### Cell 1: Complete Setup (Copy & Paste All of This)

```python
# ============================================================================
# Willowbrook Agent Tool Functions - All-in-One Cell
# Copyright (c) Microsoft. All rights reserved.
# ============================================================================

# Step 1: Imports
print("⏳ Step 1: Importing dependencies...")
from notebookutils import mssparkutils
from datetime import datetime
import json
import logging
import uuid
import time
from functools import wraps
from typing import Any, Optional
import pandas as pd

# Step 2: Configure Logging
print("⏳ Step 2: Configuring logging...")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WillowbrookTools")

# Step 3: Define Retry Decorator
print("⏳ Step 3: Setting up retry logic...")
def retry_with_timeout(max_retries: int = 3, timeout_seconds: int = 30):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt_id = str(uuid.uuid4())
            logger.info(f"🔄 Starting {func.__name__} [attempt_id: {attempt_id}]")
            
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"  Attempt {attempt}/{max_retries}...")
                    result = func(*args, **kwargs)
                    logger.info(f"✅ {func.__name__} succeeded!")
                    return result
                    
                except Exception as e:
                    logger.warning(f"  ❌ Attempt {attempt} failed: {str(e)}")
                    
                    if attempt < max_retries:
                        wait_time = 2 ** (attempt - 1)
                        logger.info(f"  ⏳ Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"  ❌ ALL {max_retries} attempts failed!")
                        raise
                        
        return wrapper
    return decorator

# Step 4: Define Tool Functions
print("⏳ Step 4: Defining tool functions...")

@retry_with_timeout(max_retries=3, timeout_seconds=30)
def list_lakehouse_files(lakehouse_path: str = "lakehouse", path: str = "/", file_extension: Optional[str] = None) -> str:
    """
    List files in the lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: "lakehouse")
        path: Sub-path within lakehouse (default: "/")
        file_extension: Filter by file extension, e.g., ".csv" (optional)
    
    Returns:
        JSON string with file list and metadata
    """
    try:
        logger.info(f"📂 Listing files in {lakehouse_path}{path}")
        
        # Get list of files
        files = mssparkutils.fs.ls(f"{lakehouse_path}{path}")
        
        # Filter by extension if provided
        if file_extension:
            filtered_files = [f for f in files if f.name.endswith(file_extension)]
            logger.info(f"  📊 Found {len(filtered_files)} files with extension {file_extension}")
        else:
            filtered_files = files
            logger.info(f"  📊 Found {len(filtered_files)} total files")
        
        # Build response
        result = {
            "success": True,
            "data": {
                "file_count": len(filtered_files),
                "files": [
                    {
                        "name": f.name,
                        "size": f.size
                    }
                    for f in filtered_files
                ],
                "timestamp": datetime.now().isoformat()
            },
            "error": None
        }
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        result = {
            "success": False,
            "data": None,
            "error": str(e)
        }
        return json.dumps(result)

@retry_with_timeout(max_retries=3, timeout_seconds=30)
def read_csv_file(lakehouse_path: str = "lakehouse", file_path: str = "/data/sample.csv", max_rows: int = 100) -> str:
    """
    Read CSV file from the lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: "lakehouse")
        file_path: Path to CSV file within lakehouse (default: "/data/sample.csv")
        max_rows: Maximum rows to return (default: 100)
    
    Returns:
        JSON string with CSV data and metadata
    """
    try:
        full_path = f"{lakehouse_path}{file_path}"
        logger.info(f"📖 Reading CSV from {full_path} (max {max_rows} rows)")
        
        # Read CSV with Spark
        df = spark.read.csv(full_path, header=True, inferSchema=True)
        total_rows = df.count()
        logger.info(f"  📊 CSV has {total_rows} total rows, {len(df.columns)} columns")
        
        # Convert to pandas and limit rows
        pdf = df.limit(max_rows).toPandas()
        
        # Build response
        result = {
            "success": True,
            "data": {
                "rows": pdf.to_dict(orient='records'),
                "columns": list(pdf.columns),
                "row_count": len(pdf),
                "total_rows": total_rows,
                "timestamp": datetime.now().isoformat()
            },
            "error": None
        }
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        result = {
            "success": False,
            "data": None,
            "error": str(e)
        }
        return json.dumps(result)

@retry_with_timeout(max_retries=3, timeout_seconds=30)
def get_lakehouse_info(lakehouse_path: str = "lakehouse") -> str:
    """
    Get metadata about the lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: "lakehouse")
    
    Returns:
        JSON string with lakehouse metadata
    """
    try:
        logger.info(f"ℹ️  Getting lakehouse info for {lakehouse_path}")
        
        # Get files
        files = mssparkutils.fs.ls(lakehouse_path)
        
        # Calculate stats
        total_size = sum(f.size for f in files)
        folder_count = sum(1 for f in files if f.name.endswith('/'))
        file_count = len(files) - folder_count
        
        logger.info(f"  📊 Files: {file_count}, Folders: {folder_count}, Total Size: {total_size} bytes")
        
        # Build response
        result = {
            "success": True,
            "data": {
                "file_count": file_count,
                "folder_count": folder_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat()
            },
            "error": None
        }
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error getting lakehouse info: {str(e)}")
        result = {
            "success": False,
            "data": None,
            "error": str(e)
        }
        return json.dumps(result)

# Step 5: Verify Everything Loaded
print("\n" + "="*70)
print("✅ ALL SETUP COMPLETE!")
print("="*70)
print(f"✓ Imports: OK")
print(f"✓ Logging: OK")
print(f"✓ Retry logic: OK")
print(f"✓ list_lakehouse_files(): {callable(list_lakehouse_files)}")
print(f"✓ read_csv_file(): {callable(read_csv_file)}")
print(f"✓ get_lakehouse_info(): {callable(get_lakehouse_info)}")
print("="*70)
print("\n📝 NOTE: All 3 tool functions are now available for use!")
print("Ready for Phase 3: Test the tool functions\n")
```

---

## That's It!

### Run This Cell

1. **Copy** the entire code block above
2. **Paste** into **Cell 1** of your Fabric notebook
3. **Run the cell** (Shift+Enter or click Run)

### Expected Output

```
⏳ Step 1: Importing dependencies...
⏳ Step 2: Configuring logging...
⏳ Step 3: Setting up retry logic...
⏳ Step 4: Defining tool functions...

======================================================================
✅ ALL SETUP COMPLETE!
======================================================================
✓ Imports: OK
✓ Logging: OK
✓ Retry logic: OK
✓ list_lakehouse_files(): True
✓ read_csv_file(): True
✓ get_lakehouse_info(): True
======================================================================

📝 NOTE: All 3 tool functions are now available for use!
Ready for Phase 3: Test the tool functions
```

---

## Installation (If Needed)

If you get a `ModuleNotFoundError`, run this in a cell **before** the setup cell:

```python
%pip install pandas openpyxl azure-ai-projects azure-identity azure-storage-file-datalake opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry
```

---

## Success Criteria for Phase 2

✅ Single cell runs without errors  
✅ All 3 functions show `True` for `callable()`  
✅ No `NameError` exceptions  
✅ Functions are ready to test  

---

## Next: Phase 3

Once this cell runs successfully, you're ready for **Phase 3: Test Tool Functions**!

In Phase 3, we'll call each function individually and verify they work correctly.
