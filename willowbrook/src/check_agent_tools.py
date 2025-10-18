# Copyright (c) Microsoft. All rights reserved.
# Check Agent Tools Registration Status

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

# Configuration
ENDPOINT = "https://marti-mgv56lom-francecentral.services.ai.azure.com/api/projects/marti-mgv56lom-francece-project"
AGENT_ID = "asst_ipZYYYbuhCMCTSx5fai4b1md"

print("=" * 70)
print("CHECK: Agent Tools Registration Status")
print("=" * 70)

try:
    # Authenticate
    credential = DefaultAzureCredential()
    project = AIProjectClient(credential=credential, endpoint=ENDPOINT)
    
    # Get agent
    print("\n⏳ Retrieving agent...")
    agent = project.agents.get_agent(AGENT_ID)
    print(f"✓ Agent found: {agent.name or AGENT_ID}")
    
    # Check tools
    print("\n⏳ Checking registered tools...")
    if hasattr(agent, 'tools') and agent.tools:
        print(f"✓ Tools found: {len(agent.tools)} tools registered\n")
        
        for i, tool in enumerate(agent.tools, 1):
            print(f"Tool {i}:")
            print(f"  Type: {tool.get('type', 'Unknown')}")
            
            if isinstance(tool, dict) and 'function' in tool:
                func = tool['function']
                print(f"  Name: {func.get('name', 'Unknown')}")
                print(f"  Description: {func.get('description', 'N/A')}")
                if 'parameters' in func:
                    params = func['parameters'].get('properties', {})
                    print(f"  Parameters: {list(params.keys())}")
            print()
    else:
        print("⚠️  NO TOOLS REGISTERED!")
        print("\nTools are NOT registered with the agent.")
        print("\nYou need to add them manually:")
        print("1. Go to https://ai.azure.com")
        print("2. Select project: proj-suk-dev-01")
        print("3. Open agent: WillowbrookAgent")
        print("4. Click 'Add Tool' or 'Tools' section")
        print("5. Register each tool using PHASE4_MANUAL_TOOL_REGISTRATION.md")
        print("\nExpected tools to register:")
        print("  1. list_lakehouse_files")
        print("  2. read_csv_file")
        print("  3. get_lakehouse_info")
    
    # Print full agent details for debugging
    print("\n" + "=" * 70)
    print("Full Agent Details (JSON):")
    print("=" * 70)
    
    agent_dict = {
        'id': agent.id,
        'name': getattr(agent, 'name', 'N/A'),
        'model': getattr(agent, 'model', 'N/A'),
        'has_tools': hasattr(agent, 'tools') and bool(agent.tools),
        'tool_count': len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0,
    }
    
    print(json.dumps(agent_dict, indent=2))
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
