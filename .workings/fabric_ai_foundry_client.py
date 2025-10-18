"""
Fabric Notebook Client for Azure AI Foundry Agent
==================================================
This code runs in a Microsoft Fabric notebook and connects to an Azure AI Foundry agent.
It uses the notebookutils credentials to authenticate.
"""

from datetime import datetime, timedelta
from azure.ai.projects import AIProjectClient


class FabricMLCredential:
    """
    Custom credential class for authenticating from Fabric to Azure AI Foundry.
    Uses Fabric's notebookutils to get tokens with the ml.azure.com scope.
    """
    
    def get_token(self, *scopes, **kwargs):
        """
        Get an authentication token using Fabric's credential system.
        
        Args:
            *scopes: Token scopes (not used, we use ml.azure.com)
            **kwargs: Additional arguments
            
        Returns:
            Token object with 'token' and 'expires_on' attributes
        """
        # Use the ml.azure.com scope for Azure AI Foundry
        token = notebookutils.credentials.getToken("https://ml.azure.com")
        
        # Set expiration to 1 hour from now
        expires_on = int((datetime.now() + timedelta(hours=1)).timestamp())
        
        # Return a token object with the expected attributes
        return type('TokenInfo', (), {
            'token': token,
            'expires_on': expires_on
        })()


def connect_to_ai_foundry(endpoint: str, agent_id: str):
    """
    Connect to Azure AI Foundry and retrieve an agent.
    
    Args:
        endpoint: The Azure AI Foundry endpoint URL
        agent_id: The ID of the agent to retrieve
        
    Returns:
        Tuple of (client, agent) if successful, (None, None) if failed
    """
    try:
        # Create the credential
        credential = FabricMLCredential()
        
        # Create the AI Project client
        client = AIProjectClient(endpoint=endpoint, credential=credential)
        print("✓ Connected to Azure AI Foundry")
        
        # Try getting the agent
        agent = client.agents.get_agent(agent_id)
        print(f"✓ Agent retrieved: {agent.id}")
        
        return client, agent
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def run_agent_conversation(client, agent, user_message: str):
    """
    Run a conversation with the agent.
    
    Args:
        client: The AIProjectClient instance
        agent: The agent object
        user_message: The message to send to the agent
        
    Returns:
        The agent's response as a string
    """
    try:
        # Create a thread
        thread = client.agents.create_thread()
        print(f"✓ Thread created: {thread.id}")
        
        # Add the user message
        message = client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        print(f"✓ Message added: {message.id}")
        
        # Run the agent
        run = client.agents.create_and_process_run(
            thread_id=thread.id,
            assistant_id=agent.id
        )
        print(f"✓ Run completed: {run.status}")
        
        # Get the messages
        messages = client.agents.list_messages(thread_id=thread.id)
        
        # Get the assistant's response (most recent message)
        for msg in messages:
            if msg.role == "assistant":
                return msg.content[0].text.value
                
        return "No response from agent"
        
    except Exception as e:
        print(f"✗ Error running conversation: {e}")
        import traceback
        traceback.print_exc()
        return None


# Example usage
if __name__ == "__main__":
    # Configuration
    ENDPOINT = "https://marti-mgv56lom-francecentral.services.ai.azure.com"
    AGENT_ID = "asst_WF3P9wa8Or3pg6I1Qu4QCMAS"
    
    # Connect to AI Foundry
    client, agent = connect_to_ai_foundry(ENDPOINT, AGENT_ID)
    
    if client and agent:
        # Run a conversation
        response = run_agent_conversation(
            client, 
            agent, 
            "List the CSV files in my lakehouse"
        )
        
        if response:
            print(f"\nAgent Response:\n{response}")
