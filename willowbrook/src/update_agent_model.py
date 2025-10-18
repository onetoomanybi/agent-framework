# Copyright (c) Microsoft. All rights reserved.
# Update agent to use gpt-4 (or another available model)

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

ENDPOINT = (
    "https://marti-mgv56lom-francecentral.services.ai.azure.com/api/projects/marti-mgv56lom-francece-project"
)
AGENT_ID = "asst_fKaNwNDTW454UMz3kHo6JGtM"

# Try different models in order of preference
MODELS_TO_TRY = ["gpt-4", "gpt-35-turbo", "gpt-4-turbo"]

print("=" * 70)
print("UPDATING AGENT MODEL")
print("=" * 70)

try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(credential=credential, endpoint=ENDPOINT)

    # Get current agent
    agent = project.agents.get_agent(AGENT_ID)
    print(f"\nCurrent agent: {agent.name}")
    print(f"Current model: {agent.model}")

    # Try to update with a different model
    for model in MODELS_TO_TRY:
        try:
            print(f"\nTrying to update agent to: {model}")
            updated_agent = project.agents.update_agent(
                agent_id=AGENT_ID,
                model=model,
            )
            print(f"✅ SUCCESS! Agent updated to: {updated_agent.model}")
            break
        except Exception as e:
            print(f"❌ Failed with {model}: {str(e)}")
            continue
    else:
        print("\n❌ Could not update to any model in list")
        print("Please check what models are available in your region")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
