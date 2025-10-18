# Copyright (c) Microsoft. All rights reserved.
# List available model deployments

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

ENDPOINT = (
    "https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01"
)

print("Checking available models in project...")

try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(credential=credential, endpoint=ENDPOINT)

    # List models
    print("\nAttempting to list models...")
    try:
        models = project.models.list()
        for model in models:
            print(f"  - {model}")
    except AttributeError:
        print("  Models API not available")

    # Get project info
    print("\nProject info available:")
    print(f"  - endpoint: {ENDPOINT}")

    # Check agent
    agent = project.agents.get_agent("asst_KjZwGAAWsrAvXLsVbMBTqZZb")
    print(f"\nCurrent agent model: {agent.model}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
