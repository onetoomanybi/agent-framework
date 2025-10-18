# Copyright (c) Microsoft. All rights reserved.
# Update all scripts to correct configuration

import os

# Correct configuration for the new project
CORRECT_ENDPOINT = (
    "https://marti-mgv56lom-francecentral.services.ai.azure.com"
)
CORRECT_AGENT_ID = "asst_WF3P9wa8Or3pg6I1Qu4QCMAS"

SCRIPT_DIR = "willowbrook/src"
FILES_TO_UPDATE = [
    "phase5_test_agent_tools.py",
    "phase6_natural_language_test.py",
    "check_agent_tools.py",
    "register_tools.py",
    "phase4_verify_agent.py",
    "investigate_api.py",
    "fix_agent_model.py",
    "update_agent_model.py",
]

print("=" * 70)
print("UPDATING ALL SCRIPTS TO CORRECT CONFIGURATION")
print("=" * 70)
print(f"\nEndpoint: {CORRECT_ENDPOINT}")
print(f"Agent ID: {CORRECT_AGENT_ID}\n")

updates_made = 0

for filename in FILES_TO_UPDATE:
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"⏭️  {filename} - NOT FOUND (skipping)")
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Track if we made changes
        original_content = content

        # Replace old agent IDs with new one
        content = content.replace(
            'AGENT_ID = "asst_KjZwGAAWsrAvXLsVbMBTqZZb"',
            f'AGENT_ID = "{CORRECT_AGENT_ID}"',
        )

        # Replace various endpoint formats
        old_endpoints = [
            "https://ait-suk-dev-01.services.ai.azure.com/api/projects/proj-suk-dev-01",
            "https://marti-mgv56lom-francece-project.openai.azure.com/api/projects/marti-mgv56lom-francece-project",
            "https://marti-mgv56lom-francece-project.openai.azure.com",
        ]

        for old_endpoint in old_endpoints:
            if old_endpoint in content:
                content = content.replace(old_endpoint, CORRECT_ENDPOINT)

        # Write back if changed
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ {filename} - Updated")
            updates_made += 1
        else:
            print(f"✓  {filename} - Already correct")

    except Exception as e:
        print(f"❌ {filename} - Error: {e}")

print("\n" + "=" * 70)
print(f"✅ COMPLETE: {updates_made} files updated")
print("=" * 70)
