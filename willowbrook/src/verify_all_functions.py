# Copyright (c) Microsoft. All rights reserved.
# Verify complete tool setup

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

ENDPOINT = (
    "https://marti-mgv56lom-francecentral.services.ai.azure.com"
    "/api/projects/marti-mgv56lom-francece-project"
)
AGENT_ID = "asst_ipZYYYbuhCMCTSx5fai4b1md"

print("=" * 70)
print("COMPLETE VERIFICATION: FUNCTIONS & TOOLS")
print("=" * 70)

try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(credential=credential, endpoint=ENDPOINT)

    # Get agent
    agent = project.agents.get_agent(AGENT_ID)

    print(f"\n✅ Agent: {agent.name}")
    print(f"   ID: {agent.id}")
    print(f"   Model: {agent.model}")

    # Check tools
    print(f"\n📋 TOOLS REGISTERED: {len(agent.tools) if agent.tools else 0}")

    if agent.tools:
        for i, tool in enumerate(agent.tools, 1):
            tool_type = tool.get("type", "unknown")
            if tool_type == "function":
                func_name = tool.get("function", {}).get("name", "Unknown")
                func_desc = tool.get("function", {}).get(
                    "description", ""
                )
                print(f"\n   {i}. {func_name}")
                print(f"      Type: function")
                print(f"      Description: {func_desc[:60]}...")
            else:
                print(f"\n   {i}. {tool_type}")

    print("\n" + "=" * 70)
    print("TOOL FUNCTIONS STATUS:")
    print("=" * 70)

    expected_tools = [
        "list_lakehouse_files",
        "read_csv_file",
        "get_lakehouse_info",
    ]

    tool_names = [
        tool.get("function", {}).get("name")
        for tool in (agent.tools or [])
        if tool.get("type") == "function"
    ]

    for tool_name in expected_tools:
        if tool_name in tool_names:
            print(f"✅ {tool_name}")
        else:
            print(f"❌ {tool_name} - NOT FOUND")

    print("\n" + "=" * 70)
    if len(tool_names) == 3 and all(
        t in tool_names for t in expected_tools
    ):
        print("✅ ALL 3 FUNCTIONS REGISTERED AND READY!")
    else:
        print(f"⚠️  Only {len(tool_names)} tools found (expected 3)")
    print("=" * 70)

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
