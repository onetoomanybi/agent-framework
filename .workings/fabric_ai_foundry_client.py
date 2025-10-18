"""
Fabric Notebook Client for Azure AI Foundry Agent
==================================================
This code runs in a Microsoft Fabric notebook and connects to an Azure AI Foundry agent.
It uses the notebookutils credentials to authenticate.
"""

from datetime import datetime, timedelta
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Handle notebookutils which is only available in Fabric notebooks
try:
    # In Fabric notebook environment - notebookutils is a built-in
    import notebookutils
except ImportError:
    # For local testing or non-Fabric environments - provide a mock
    class MockNotebookUtils:
        """Mock notebookutils for testing outside Fabric notebooks"""
        
        class credentials:
            @staticmethod
            def getToken(scope: str) -> str:
                """
                Mock credential for testing.
                In real Fabric notebooks, this returns a valid Azure token.
                For testing, returns a placeholder token.
                
                Args:
                    scope: The token scope (e.g., "https://ml.azure.com")
                    
                Returns:
                    A token string (mock for testing)
                """
                return "mock-token-for-testing-local-development"
    
    # Use the mock when running outside Fabric
    notebookutils = MockNotebookUtils()


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


def connect_to_ai_foundry(endpoint: str, agent_id: str, use_default_credential: bool = False):
    """
    Connect to Azure AI Foundry and retrieve an agent.
    
    Args:
        endpoint: The Azure AI Foundry endpoint URL (e.g., "https://your-project.cognitiveservices.azure.com")
        agent_id: The ID of the agent to retrieve
        use_default_credential: If True, use DefaultAzureCredential (modern pattern).
                               If False (default), use Fabric notebookutils credential.
        
    Returns:
        Tuple of (client, agent) if successful, (None, None) if failed
    """
    try:
        # Choose credential based on environment
        if use_default_credential:
            # Modern pattern: Use DefaultAzureCredential
            # Works with: environment variables, managed identity, Azure CLI, etc.
            credential = DefaultAzureCredential()
            print("✓ Using DefaultAzureCredential (modern pattern)")
        else:
            # Fabric pattern: Use notebookutils
            # Works in Fabric notebooks and for local testing with mock
            credential = FabricMLCredential()
            print("✓ Using Fabric notebookutils credential")
        
        # Create the AI Project client with modern endpoint parameter
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
