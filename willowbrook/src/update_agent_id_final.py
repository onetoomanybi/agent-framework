# Copyright (c) Microsoft. All rights reserved.
# Final configuration update

import os

ENDPOINT = (
    "https://marti-mgv56lom-francecentral.services.ai.azure.com"
    "/api/projects/marti-mgv56lom-francece-project"
)
AGENT_ID = "asst_ipZYYYbuhCMCTSx5fai4b1md"

SCRIPT_DIR = "willowbrook/src"
FILES_TO_UPDATE = [
    "phase5_test_agent_tools.py",
    "phase6_natural_language_test.py",
    "check_agent_tools.py",
    "register_tools.py",
    "phase4_verify_agent.py",
]

print(f"Updating to Agent ID: {AGENT_ID}\n")

for filename in FILES_TO_UPDATE:
    filepath = os.path.join(SCRIPT_DIR, filename)
    if not os.path.exists(filepath):
        continue

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace any agent ID
        content = content.replace(
            'AGENT_ID = "asst_fKaNwNDTW454UMz3kHo6JGtM"',
            f'AGENT_ID = "{AGENT_ID}"',
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ {filename}")

    except Exception as e:
        print(f"❌ {filename}: {e}")

print(f"\n✅ All files updated with Agent ID: {AGENT_ID}")
