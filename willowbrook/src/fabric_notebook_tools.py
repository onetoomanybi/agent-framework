# Copyright (c) Microsoft. All rights reserved.

"""
Fabric Notebook Implementation of Agent Tools
==============================================
This code runs directly in a Microsoft Fabric notebook.
It provides the agent tool implementations as callable functions.
No external Azure infrastructure needed - uses Fabric lakehouse as storage.
"""

import json
import io
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import time
import functools

# Fabric notebook environment
try:
    from notebookutils.mssparkutils import fs as mssparkutils_fs
except ImportError:
    # For testing outside Fabric
    mssparkutils_fs = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_with_timeout(max_retries: int = 3, timeout_seconds: float = 30.0):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout_seconds: Timeout in seconds for each attempt
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt_id = str(uuid.uuid4())[:8]
            logger.info(f"Starting operation {func.__name__} (attempt_id: {attempt_id})")
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"Operation {func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                except Exception as e:
                    last_exception = e
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time}s... (attempt_id: {attempt_id})"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
            
            logger.error(
                f"Operation {func.__name__} failed after {max_retries} attempts "
                f"(attempt_id: {attempt_id}): {str(last_exception)}"
            )
            raise last_exception
        return wrapper
    return decorator


@retry_with_timeout(max_retries=3, timeout_seconds=30.0)
def list_lakehouse_files(
    lakehouse_path: str = "/Workspace/Lakehouses/default",
    path: str = "Files",
    file_extension: Optional[str] = None
) -> str:
    """
    List files in the Fabric lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse (default: current workspace default)
        path: Subdirectory within lakehouse (e.g., "Files", "Files/data")
        file_extension: Optional filter for file extension (e.g., ".csv")
    
    Returns:
        JSON string with file list
    """
    logger.info(f"Listing files in {lakehouse_path}/{path}")
    
    try:
        # Construct full path
        full_path = f"{lakehouse_path}/{path}"
        
        # List files using Fabric's file system
        files = mssparkutils_fs.ls(full_path)
        
        # Filter and process files
        file_list: List[Dict[str, Any]] = []
        for file_info in files:
            name = file_info.name
            size = file_info.size if hasattr(file_info, 'size') else 0
            last_modified = file_info.modificationTime if hasattr(file_info, 'modificationTime') else None
            
            # Apply extension filter if provided
            if file_extension and not name.endswith(file_extension):
                continue
            
            file_list.append({
                "name": name,
                "size": size,
                "last_modified": datetime.fromtimestamp(last_modified / 1000).isoformat() if last_modified else None
            })
        
        result = {
            "success": True,
            "file_count": len(file_list),
            "files": file_list
        }
        
        logger.info(f"Successfully listed {len(file_list)} files")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@retry_with_timeout(max_retries=3, timeout_seconds=30.0)
def read_csv_file(
    lakehouse_path: str = "/Workspace/Lakehouses/default",
    file_path: str = "Files/data.csv",
    max_rows: int = 100
) -> str:
    """
    Read a CSV file from the Fabric lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse
        file_path: Path to the CSV file within lakehouse
        max_rows: Maximum rows to return (default 100)
    
    Returns:
        JSON string with CSV data
    """
    logger.info(f"Reading CSV file {file_path}")
    
    try:
        # Construct full path
        full_path = f"{lakehouse_path}/{file_path}"
        
        # Read file using Spark
        df = spark.read.csv(full_path, header=True, inferSchema=True)
        
        # Limit rows
        df_limited = df.limit(max_rows)
        
        # Convert to pandas for easier JSON serialization
        pdf = df_limited.toPandas()
        
        result = {
            "success": True,
            "row_count": len(pdf),
            "total_rows": df.count(),
            "headers": list(pdf.columns),
            "data": pdf.to_dict('records')
        }
        
        logger.info(f"Successfully read {len(pdf)} rows from {file_path}")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@retry_with_timeout(max_retries=3, timeout_seconds=30.0)
def get_lakehouse_info(
    lakehouse_path: str = "/Workspace/Lakehouses/default"
) -> str:
    """
    Get metadata about the Fabric lakehouse.
    
    Args:
        lakehouse_path: Path to the lakehouse
    
    Returns:
        JSON string with lakehouse metadata
    """
    logger.info(f"Getting lakehouse info for {lakehouse_path}")
    
    try:
        # Get directory listing
        items = mssparkutils_fs.ls(lakehouse_path)
        
        # Count files and folders
        file_count = 0
        folder_count = 0
        total_size = 0
        
        for item in items:
            if item.name.endswith('/'):
                folder_count += 1
            else:
                file_count += 1
                total_size += item.size if hasattr(item, 'size') else 0
        
        result = {
            "success": True,
            "lakehouse_path": lakehouse_path,
            "file_count": file_count,
            "folder_count": folder_count,
            "total_size_bytes": total_size,
            "last_accessed": datetime.now().isoformat()
        }
        
        logger.info(f"Lakehouse info retrieved: {file_count} files, {folder_count} folders")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error getting lakehouse info: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# Export functions as agent tools
__all__ = [
    'list_lakehouse_files',
    'read_csv_file',
    'get_lakehouse_info'
]
