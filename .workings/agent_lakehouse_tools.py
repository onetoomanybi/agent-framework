"""
Agent Tool Implementation for Fabric Lakehouse Access
======================================================
This code runs in Azure AI Foundry as part of agent tools.
It authenticates to Fabric and reads files from a lakehouse.
"""

import json
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.filedatalake import DataLakeServiceClient
from typing import List, Dict


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
    file_extension: str = None
) -> str:
    """
    List files in a Fabric lakehouse.
    
    Args:
        workspace_id: The Fabric workspace ID (GUID)
        lakehouse_id: The lakehouse ID (GUID)
        path: Path within the lakehouse (default: "Files")
        file_extension: Optional filter by file extension (e.g., ".csv")
        
    Returns:
        JSON string containing list of files
    """
    try:
        # Create credential
        credential = FabricLakehouseCredential()
        
        # Connect to OneLake (Fabric's data lake)
        datalake_client = DataLakeServiceClient(
            account_url="https://onelake.dfs.fabric.microsoft.com",
            credential=credential
        )
        
        # Get the file system client for the workspace
        fs_client = datalake_client.get_file_system_client(workspace_id)
        
        # Build the full path
        full_path = f"{lakehouse_id}/{path}"
        
        # List paths
        paths = fs_client.get_paths(path=full_path)
        
        # Filter files
        files = []
        for p in paths:
            # Skip directories
            if not p.is_directory:
                # Apply extension filter if specified
                if file_extension is None or p.name.endswith(file_extension):
                    files.append({
                        "name": p.name,
                        "size": p.content_length,
                        "last_modified": p.last_modified.isoformat() if p.last_modified else None
                    })
        
        return json.dumps({
            "success": True,
            "file_count": len(files),
            "files": files
        })
        
    except Exception as e:
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
    try:
        # Create credential
        credential = FabricLakehouseCredential()
        
        # Connect to OneLake
        datalake_client = DataLakeServiceClient(
            account_url="https://onelake.dfs.fabric.microsoft.com",
            credential=credential
        )
        
        # Get the file system client
        fs_client = datalake_client.get_file_system_client(workspace_id)
        
        # Build the full path
        full_path = f"{lakehouse_id}/{file_path}"
        
        # Get file client
        file_client = fs_client.get_file_client(full_path)
        
        # Download the file
        download = file_client.download_file()
        content = download.readall()
        
        # Decode content
        text_content = content.decode('utf-8')
        
        # Parse CSV (basic parsing)
        lines = text_content.strip().split('\n')
        
        if len(lines) == 0:
            return json.dumps({
                "success": False,
                "error": "File is empty"
            })
        
        # First line is header
        headers = lines[0].split(',')
        
        # Parse remaining lines
        rows = []
        for line in lines[1:]:
            values = line.split(',')
            row = {headers[i].strip(): values[i].strip() for i in range(min(len(headers), len(values)))}
            rows.append(row)
        
        return json.dumps({
            "success": True,
            "row_count": len(rows),
            "headers": headers,
            "data": rows[:100]  # Return first 100 rows
        })
        
    except Exception as e:
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
