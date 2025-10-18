# Copyright (c) Microsoft. All rights reserved.
# Check if agent exists in new project

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

ENDPOINT = (
    "https://marti-mgv56lom-francece-"
    "project.openai.azure.com/api/projects/"
    "marti-mgv56lom-francece-project"
)

print("=" * 70)
print("CHECKING FOR AGENT IN NEW PROJECT")
print("=" * 70)

try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(credential=credential, endpoint=ENDPOINT)

    print("\nLooking for WillowbrookFabricAgent...")

    # Try to get the agent from old ID
    OLD_AGENT_ID = "asst_KjZwGAAWsrAvXLsVbMBTqZZb"
    try:
        agent = project.agents.get_agent(OLD_AGENT_ID)
        print(f"✅ FOUND! Agent exists in new project")
        print(f"   Name: {agent.name}")
        print(f"   ID: {agent.id}")
        print(f"   Model: {agent.model}")
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"❌ Agent {OLD_AGENT_ID} not found in new project")
            print("\n⏳ Will need to create new agent in this project")
        else:
            print(f"❌ Error: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
