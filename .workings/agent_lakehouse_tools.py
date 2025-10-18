"""
Agent Tool Implementation for Fabric Lakehouse Access
======================================================
This code runs in Azure AI Foundry as part of agent tools.
It authenticates to Fabric and reads files from a lakehouse.
"""

import json
import io
import logging
import pandas as pd
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.filedatalake import DataLakeServiceClient
from typing import List, Dict
import time
import functools
import uuid

# Configure logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_with_timeout(max_retries: int = 3, timeout_seconds: float = 30.0):
    """
    Decorator for retry logic with exponential backoff and timeout.
    
    Args:
        max_retries: Maximum number of retry attempts
        timeout_seconds: Timeout in seconds for each attempt
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt_id = str(uuid.uuid4())[:8]
            logger.info(f"Starting operation {func.__name__} (attempt_id: {attempt_id})")
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    # Add timeout to the operation
                    import asyncio
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                    logger.info(f"Operation {func.__name__} succeeded on attempt {attempt + 1}")
                    return result
                except asyncio.TimeoutError:
                    last_exception = TimeoutError(f"Operation timed out after {timeout_seconds}s")
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Attempt {attempt + 1} timed out for {func.__name__}. "
                        f"Retrying in {wait_time}s... (attempt_id: {attempt_id})"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                except Exception as e:
                    last_exception = e
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time}s... (attempt_id: {attempt_id})"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
            
            # All retries exhausted
            logger.error(
                f"Operation {func.__name__} failed after {max_retries} attempts "
                f"(attempt_id: {attempt_id}): {str(last_exception)}"
            )
            raise last_exception
        return wrapper
    return decorator


class FabricLakehouseCredential:
    """
    Credential class for authenticating from Azure AI Foundry to Fabric.
    This uses Azure managed identity or service principal.
    """
    
    def get_token(self, *scopes, **kwargs):
        """
        Get an authentication token for accessing Fabric.
        
        Args:
            *scopes: Token scopes
            **kwargs: Additional arguments
            
        Returns:
            Token object from Azure Identity
        """
        # Use DefaultAzureCredential which tries multiple auth methods:
        # 1. Managed Identity (if deployed in Azure)
        # 2. Service Principal via environment variables
        # 3. Azure CLI credentials (for local development)
        cred = DefaultAzureCredential()
        
        # Fabric uses the Power BI API scope
        token = cred.get_token("https://analysis.windows.net/powerbi/api/.default")
        return token


async def list_lakehouse_files(
    workspace_id: str,
    lakehouse_id: str,
    path: str = "Files",
    file_extension: str = None,
    limit: int = 100,
    offset: int = 0
) -> str:
    """
    List files in a Fabric lakehouse with pagination.

    Args:
        workspace_id: The Fabric workspace ID (GUID)
            Example: "12345678-1234-5678-1234-567812345678"
        lakehouse_id: The lakehouse ID (GUID)
            Example: "87654321-4321-8765-4321-876543218765"
        path: Path within the lakehouse (default: "Files")
        file_extension: Optional filter by file extension (e.g., ".csv")
        limit: Maximum number of files to return (default: 100)
        offset: Number of files to skip for pagination (default: 0)

    Returns:
        JSON string containing list of files with pagination info
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{request_id}] Listing files in workspace {workspace_id}, "
        f"lakehouse {lakehouse_id}, path {path}"
    )
    
    try:
        # Create credential
        credential = FabricLakehouseCredential()
        logger.debug(f"[{request_id}] Created FabricLakehouseCredential")

        # Connect to OneLake (Fabric's data lake)
        datalake_client = DataLakeServiceClient(
            account_url="https://onelake.dfs.fabric.microsoft.com",
            credential=credential
        )
        logger.debug(f"[{request_id}] Connected to OneLake")

        # Get the file system client for the workspace
        fs_client = datalake_client.get_file_system_client(workspace_id)
        logger.debug(
            f"[{request_id}] Got file system client for workspace {workspace_id}"
        )

        # Build the full path
        full_path = f"{lakehouse_id}/{path}"
        logger.debug(f"[{request_id}] Listing path: {full_path}")

        # List paths
        paths = fs_client.get_paths(path=full_path)

        # Filter files and apply pagination
        all_files = []
        for p in paths:
            # Skip directories
            if not p.is_directory:
                # Apply extension filter if specified
                if (file_extension is None or
                        p.name.endswith(file_extension)):
                    all_files.append({
                        "name": p.name,
                        "size": p.content_length,
                        "last_modified": (
                            p.last_modified.isoformat()
                            if p.last_modified else None
                        )
                    })

        # Apply pagination
        total_count = len(all_files)
        paginated_files = all_files[offset:offset + limit]
        has_more = (offset + limit) < total_count

        logger.info(
            f"[{request_id}] Listed {len(paginated_files)} of "
            f"{total_count} files (offset: {offset}, has_more: {has_more})"
        )

        return json.dumps({
            "success": True,
            "file_count": len(paginated_files),
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": has_more,
            "files": paginated_files
        })
        
    except Exception as e:
        logger.error(f"[{request_id}] Error listing files: {str(e)}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def read_csv_file(
    workspace_id: str,
    lakehouse_id: str,
    file_path: str
) -> str:
    """
    Read a CSV file from a Fabric lakehouse.
    
    Args:
        workspace_id: The Fabric workspace ID (GUID)
        lakehouse_id: The lakehouse ID (GUID)
        file_path: Path to the CSV file within the lakehouse
        
    Returns:
        JSON string containing CSV data or error
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{request_id}] Reading CSV file from workspace {workspace_id}, "
        f"lakehouse {lakehouse_id}, file {file_path}"
    )
    
    try:
        # Create credential
        credential = FabricLakehouseCredential()
        logger.debug(f"[{request_id}] Created FabricLakehouseCredential")
        
        # Connect to OneLake
        datalake_client = DataLakeServiceClient(
            account_url="https://onelake.dfs.fabric.microsoft.com",
            credential=credential
        )
        logger.debug(f"[{request_id}] Connected to OneLake")
        
        # Get the file system client
        fs_client = datalake_client.get_file_system_client(workspace_id)
        logger.debug(
            f"[{request_id}] Got file system client for workspace "
            f"{workspace_id}"
        )
        
        # Build the full path
        full_path = f"{lakehouse_id}/{file_path}"
        logger.debug(f"[{request_id}] Full path: {full_path}")
        
        # Get file client
        file_client = fs_client.get_file_client(full_path)
        logger.debug(f"[{request_id}] Got file client")
        
        # Download the file
        download = file_client.download_file()
        content = download.readall()
        logger.debug(f"[{request_id}] Downloaded file ({len(content)} bytes)")
        
        # Use pandas for robust CSV parsing
        # Handles: quoted fields, escaped commas, various encodings, line breaks
        df = pd.read_csv(io.BytesIO(content))
        logger.debug(f"[{request_id}] Parsed CSV with {len(df)} rows")
        
        # Convert to dictionary format for JSON serialization
        data = df.head(100).to_dict(orient='records')
        
        logger.info(
            f"[{request_id}] Successfully read CSV file with "
            f"{len(df)} rows, returning {len(data)} records"
        )
        
        return json.dumps({
            "success": True,
            "row_count": len(df),
            "headers": df.columns.tolist(),
            "data": data
        })
        
    except Exception as e:
        logger.error(
            f"[{request_id}] Error reading CSV file: {str(e)}",
            exc_info=True
        )
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def get_lakehouse_info(workspace_id: str, lakehouse_id: str) -> str:
    """
    Get information about a lakehouse.
    
    Args:
        workspace_id: The Fabric workspace ID (GUID)
        lakehouse_id: The lakehouse ID (GUID)
        
    Returns:
        JSON string containing lakehouse information
    """
    try:
        credential = FabricLakehouseCredential()
        
        datalake_client = DataLakeServiceClient(
            account_url="https://onelake.dfs.fabric.microsoft.com",
            credential=credential
        )
        
        fs_client = datalake_client.get_file_system_client(workspace_id)
        
        # Get properties
        properties = fs_client.get_file_system_properties()
        
        return json.dumps({
            "success": True,
            "workspace_id": workspace_id,
            "lakehouse_id": lakehouse_id,
            "last_modified": properties.last_modified.isoformat() if properties.last_modified else None
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# Tool function mapping for OpenAPI spec
TOOL_FUNCTIONS = {
    "listFiles": list_lakehouse_files,
    "readCSVFile": read_csv_file,
    "getLakehouseInfo": get_lakehouse_info
}
