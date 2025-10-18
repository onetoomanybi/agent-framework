"""
Azure Function App Implementation for Agent Tools
==================================================
This code runs as Azure Functions and hosts the agent tool endpoints.
Each function corresponds to an operation in the OpenAPI spec.
"""

import json
import logging
import azure.functions as func
from agent_lakehouse_tools import list_lakehouse_files, read_csv_file, get_lakehouse_info

# Create the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="listFiles", methods=["POST"])
async def list_files_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function endpoint for listing lakehouse files.
    """
    logging.info('Processing listFiles request')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Extract parameters
        workspace_id = req_body.get('workspace_id')
        lakehouse_id = req_body.get('lakehouse_id')
        path = req_body.get('path', 'Files')
        file_extension = req_body.get('file_extension')
        
        # Validate required parameters
        if not workspace_id or not lakehouse_id:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "workspace_id and lakehouse_id are required"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Call the tool function
        result = await list_lakehouse_files(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
            path=path,
            file_extension=file_extension
        )
        
        return func.HttpResponse(
            result,
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Invalid request body"
            }),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="readCSVFile", methods=["POST"])
async def read_csv_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function endpoint for reading CSV files.
    """
    logging.info('Processing readCSVFile request')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Extract parameters
        workspace_id = req_body.get('workspace_id')
        lakehouse_id = req_body.get('lakehouse_id')
        file_path = req_body.get('file_path')
        
        # Validate required parameters
        if not workspace_id or not lakehouse_id or not file_path:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "workspace_id, lakehouse_id, and file_path are required"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Call the tool function
        result = await read_csv_file(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id,
            file_path=file_path
        )
        
        return func.HttpResponse(
            result,
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Invalid request body"
            }),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="getLakehouseInfo", methods=["POST"])
async def get_info_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function endpoint for getting lakehouse information.
    """
    logging.info('Processing getLakehouseInfo request')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Extract parameters
        workspace_id = req_body.get('workspace_id')
        lakehouse_id = req_body.get('lakehouse_id')
        
        # Validate required parameters
        if not workspace_id or not lakehouse_id:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": "workspace_id and lakehouse_id are required"
                }),
                status_code=400,
                mimetype="application/json"
            )
        
        # Call the tool function
        result = await get_lakehouse_info(
            workspace_id=workspace_id,
            lakehouse_id=lakehouse_id
        )
        
        return func.HttpResponse(
            result,
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": "Invalid request body"
            }),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for monitoring.
    """
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "fabric-lakehouse-tools"
        }),
        status_code=200,
        mimetype="application/json"
    )
