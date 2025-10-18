# Copyright (c) Microsoft. All rights reserved.
# Update all scripts to use new project

import os
import re

# New project configuration
NEW_ENDPOINT = (
    "https://marti-mgv56lom-francece-"
    "project.openai.azure.com/api/projects/"
    "marti-mgv56lom-francece-project"
)
OLD_ENDPOINT = (
    "https://ait-suk-dev-01.services.ai.azure.com/api/"
    "projects/proj-suk-dev-01"
)

SCRIPT_DIR = "willowbrook/src"
FILES_TO_UPDATE = [
    "phase5_test_agent_tools.py",
    "phase6_natural_language_test.py",
    "check_agent_tools.py",
    "register_tools.py",
]

print("=" * 70)
print("UPDATING SCRIPTS TO NEW PROJECT")
print("=" * 70)
print(f"\nOld endpoint: {OLD_ENDPOINT[:50]}...")
print(f"New endpoint: {NEW_ENDPOINT[:50]}...")

for filename in FILES_TO_UPDATE:
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"\n❌ {filename} - NOT FOUND")
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace endpoint
        updated_content = content.replace(OLD_ENDPOINT, NEW_ENDPOINT)

        # Save back
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"✅ {filename} - Updated")

    except Exception as e:
        print(f"❌ {filename} - Error: {e}")

print("\n" + "=" * 70)
print("✅ SCRIPT UPDATES COMPLETE")
print("=" * 70)
