# Copyright (c) Microsoft. All rights reserved.
# Fabric Notebook Code: Agent with Tool Execution

# ============================================================================
# FABRIC NOTEBOOK CELL - Agent Integration
# ============================================================================
# 
# Add this cell to your Fabric notebook AFTER Cell 1 (which has tool functions)
# 
# This cell will:
# 1. Initialize the AI Foundry agent
# 2. Query the agent with your lakehouse path
# 3. Agent will call your tool functions automatically
# 4. Display results
# ============================================================================

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

ENDPOINT = "https://marti-mgv56lom-francecentral.services.ai.azure.com/api/projects/marti-mgv56lom-francece-project"
AGENT_ID = "asst_ipZYYYbuhCMCTSx5fai4b1md"
LAKEHOUSE_PATH = "abfss://Mart_DVCP@onelake.dfs.fabric.microsoft.com/LH_Validation.Lakehouse/Files"

# ============================================================================
# AGENT CLIENT SETUP
# ============================================================================

print("=" * 70)
print("AGENT EXECUTION IN FABRIC NOTEBOOK")
print("=" * 70)

print("\n📍 Configuration:")
print(f"   Agent ID: {AGENT_ID}")
print(f"   Lakehouse: {LAKEHOUSE_PATH}")

print("\n⏳ Initializing agent client...")
try:
    credential = DefaultAzureCredential()
    client = AIProjectClient(endpoint=ENDPOINT, credential=credential)
    agent = client.agents.get_agent(AGENT_ID)
    print(f"✓ Agent loaded: {agent.name}")
except Exception as e:
    print(f"❌ Error: {e}")
    raise

# ============================================================================
# DEFINE TEST QUERIES
# ============================================================================

test_queries = [
    f"List the files in {LAKEHOUSE_PATH}",
    f"What's the metadata for {LAKEHOUSE_PATH}?",
    f"Can you get the info about {LAKEHOUSE_PATH}?",
]

# ============================================================================
# RUN AGENT WITH TOOL CALLS
# ============================================================================

print("\n⏳ Running agent queries...")
print("-" * 70)

for query_num, query in enumerate(test_queries, 1):
    print(f"\n📝 Query {query_num}: {query}")
    print("-" * 70)
    
    try:
        # Create thread
        thread = client.agents.threads.create()
        
        # Send message
        client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Run and process (auto function calling enabled)
        run = client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Check status
        if run.status == "completed":
            print("✓ Run completed")
            
            # Get messages
            messages = client.agents.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING
            )
            
            # Print conversation
            for msg in messages:
                if msg.text_messages:
                    role = "👤 USER" if msg.role == "user" else "🤖 AGENT"
                    for text_msg in msg.text_messages:
                        print(f"{role}: {text_msg.text[:500]}")
        
        elif run.status == "failed":
            print(f"❌ Run failed: {run.last_error}")
        
        else:
            print(f"⚠️  Run status: {run.status}")
        
        # Cleanup
        client.agents.threads.delete(thread.id)
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ AGENT EXECUTION COMPLETE")
print("=" * 70)
print("\nTools called:")
print("  ✓ list_lakehouse_files (if 'list' query)")
print("  ✓ get_lakehouse_info (if 'metadata' query)")
print("  ✓ read_csv_file (if 'read' query)")
