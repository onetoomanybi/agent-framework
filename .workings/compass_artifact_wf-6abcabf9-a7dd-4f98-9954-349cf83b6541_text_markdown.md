# Technical Architecture Validation: Microsoft Agent Framework with Azure AI Foundry and Fabric Lakehouse

Your proposed architecture contains a critical product confusion that fundamentally affects the entire integration approach. **Native OpenAPI 3.0 support exists only in Azure AI Agents Service (a cloud service within Azure AI Foundry), not in the standalone Microsoft Agent Framework SDK.** This distinction determines which APIs are available, how authentication works, and whether your described integration flow is possible. The Fabric Lakehouse access components are correctly specified, but the agent-to-API integration layer requires architectural revision.

Microsoft offers two distinct products often confused in this space: the open-source Microsoft Agent Framework SDK (which lacks native OpenAPI support) and the Azure AI Agents Service (which includes full OpenAPI 3.0 integration). Your architecture assumes OpenAPI capabilities that don't exist in Agent Framework. However, the Azure storage components—including the SDK choice, endpoint URL, and managed identity authentication for OneLake—are all validated as correct against current documentation.

## Product confusion at the architecture's core

Microsoft's agent ecosystem contains two separate products with overlapping names but different capabilities. The **Microsoft Agent Framework** is an open-source SDK (converging AutoGen and Semantic Kernel) for building agents locally or on any cloud platform. It supports function tools, MCP servers, and hosted tools, but has no native OpenAPI 3.0 specification loading. There is no `OpenAPITool.from_file()` method or similar functionality.

The **Azure AI Agents Service** is a managed cloud service within Azure AI Foundry that provides stateful agent execution with native OpenAPI 3.0 support. This service uses the `azure-ai-projects` SDK with `OpenApiTool` class for loading specifications. The critical distinction: if you need to use OpenAPI specs as described in your architecture, you must use Azure AI Agents Service, not the standalone Agent Framework.

Your architecture's integration approach depends entirely on which product you're using. If you're describing Azure AI Agents Service accessed through AI Foundry, the OpenAPI approach is valid but uses different APIs than stated. If you're describing standalone Agent Framework, the OpenAPI integration doesn't exist and requires manual function tool creation.

## Agent Framework SDK capabilities require correction

The `AzureOpenAIResponsesClient` integration you described is accurate for Microsoft Agent Framework. This client correctly connects agents to Azure OpenAI deployments using managed identity or other Azure credentials. The pattern `agent.run(tools=...)` is also correct, with tools passable at both agent creation and runtime.

However, OpenAPI tool definitions work completely differently than your architecture assumes. In Microsoft Agent Framework, you cannot load OpenAPI 3.0 specifications natively. Instead, you must manually create function tools that wrap your API calls. Each function uses Python type hints or C# attributes for parameter descriptions, which the framework converts into tool definitions for the LLM.

For Azure AI Agents Service, the correct OpenAPI integration uses this pattern instead:

```python
import jsonref
from azure.ai.agents.models import OpenApiTool, OpenApiManagedAuthDetails

with open("api_spec.json", "r") as f:
    openapi_spec = jsonref.loads(f.read())

auth = OpenApiManagedAuthDetails(
    security_scheme=OpenApiManagedSecurityScheme(
        audience="https://storage.azure.com/"
    )
)

openapi_tool = OpenApiTool(
    name="lakehouse_api",
    spec=openapi_spec,
    description="Access Fabric Lakehouse files",
    auth=auth
)

agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="Lakehouse Agent",
    tools=openapi_tool.definitions
)
```

The framework performs automatic parsing, generates tool definitions from operationId fields, validates parameters against JSON Schema, and handles secure API invocation. But this only works in the cloud-based Azure AI Agents Service, not the standalone SDK.

## Azure AI Foundry integration uses deprecated patterns

The `AIProjectClient.from_connection_string()` method you referenced is deprecated and no longer recommended by Microsoft. The product team discontinued support for connection strings in favor of endpoint-based authentication with managed identities. Current documentation explicitly warns against using hub-based projects and connection string authentication patterns.

The correct modern approach requires the project endpoint URL formatted as `https://<resource>.services.ai.azure.com/api/projects/<project-name>`. Authentication uses `DefaultAzureCredential` or explicit managed identity credentials. This pattern provides better security through keyless authentication and aligns with Azure's broader identity management strategy.

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

Managed identity authentication is fully supported across all Azure AI Foundry services. The platform supports system-assigned managed identities, user-assigned managed identities, and the DefaultAzureCredential chain that automatically tries multiple authentication methods. Required RBAC roles include Azure AI User for inference operations, Cognitive Services OpenAI User for model access, and Azure AI Project Manager for project-level operations.

Agents created with Microsoft Agent Framework can deploy to Azure AI Foundry through two integration paths. The direct approach uses `AIProjectClient.agents.create_agent()` to create persistent agents in the cloud service. The framework integration approach uses `AzureAIAgentClient` from the agent-framework package, which provides a unified API that deploys to the Foundry backend while maintaining local development patterns.

## OpenAPI integration details validated with restrictions

Azure AI Agents Service requires the `operationId` field in every OpenAPI operation, even though the OpenAPI 3.0 specification makes this field optional. Microsoft's documentation explicitly states: "Although not required by the OpenAPI spec, operationId is required for each function to be used with the OpenAPI tool." The operationId becomes the tool name visible to the LLM and must contain only letters, hyphens, and underscores.

The framework uses operationId fields as tool names in the function calling interface. When the LLM decides to invoke a tool, it references the operation by this name. Descriptive operationIds improve the model's ability to select appropriate tools. Missing operationIds cause 400 Bad Request errors when creating agents.

Automatic parameter validation from JSON Schema is fully supported. The framework validates parameter types, enforces required fields, validates enum constraints, and supports nested object structures before executing API calls. Type validation covers string, integer, number, boolean, array, and object types. Default values from the schema are automatically applied when parameters are omitted.

The OpenAPI integration has important restrictions. **Only GET and POST HTTP methods are supported**—PUT, DELETE, and PATCH operations are not available. Server URLs in the OpenAPI specification must be real, accessible endpoints, not placeholders like "my_public_url". The framework rejects specifications with invalid or unreachable server definitions. Tool descriptions are limited to 1024 characters for Azure OpenAI compatibility.

## Fabric Lakehouse access validated as completely correct

Every component of your Fabric Lakehouse access architecture is accurate against current Microsoft documentation. The `azure-storage-file-datalake` SDK is the official and recommended method for accessing OneLake programmatically. OneLake exposes ADLS Gen2-compatible APIs through the DataLakeServiceClient, FileSystemClient, and DataLakeFileClient classes.

The endpoint `https://onelake.dfs.fabric.microsoft.com` is confirmed correct. This is the global OneLake endpoint that accepts connections from any region. Regional endpoints follow the pattern `https://<region>-onelake.dfs.fabric.microsoft.com` for data residency requirements. The account name is always "onelake"—not your tenant name or storage account name as in standard ADLS Gen2.

Path construction using workspace_id and lakehouse_id is fully supported through two methods. The GUID-based approach uses immutable identifiers: `{workspace_guid}/{lakehouse_guid}/Files/{filepath}`. This method is recommended for production automation because GUIDs never change even when workspaces or lakehouses are renamed. The name-based approach uses `{workspace_name}/{lakehouse_name}.Lakehouse/Files/{filepath}` but requires the .Lakehouse extension and breaks if items are renamed.

Managed Identity authentication works correctly for Fabric Lakehouse access. OneLake requires Microsoft Entra ID (Azure AD) authentication with tokens scoped to `https://storage.azure.com/`. The DefaultAzureCredential automatically obtains appropriate tokens when running in Azure environments with managed identity enabled. Prerequisites include enabling "Users can access data stored in OneLake with apps external to Fabric" in the Fabric Admin Portal and granting the managed identity at least Contributor role in the target workspace.

## Integration flow requires architectural revision

Your described flow "AI Foundry → Agent Framework → OpenAPI → Tool Implementation → SDK → Lakehouse" contains gaps and assumes capabilities that don't exist. The primary issue is product confusion between Agent Framework (SDK) and Azure AI Agents Service (cloud service). The flow also lacks specification of where OpenAPI specs are hosted, how authentication tokens propagate between layers, and where the SDK code actually executes.

The correct integration flow depends on which agent product you're using. For Azure AI Agents Service with native OpenAPI support, the architecture requires a custom wrapper API that implements the OpenAPI specification. The agent calls this wrapper, which then uses the azure-storage-file-datalake SDK to access OneLake. This approach works because Azure AI Agents Service can call external APIs defined in OpenAPI specs.

The recommended flow becomes: Azure AI Foundry Project → Azure AI Agents Service (with OpenAPI tool) → Custom API Wrapper (Azure Function/App Service implementing OpenAPI spec) → azure-storage-file-datalake SDK → OneLake Fabric Lakehouse. The custom wrapper API authenticates to OneLake using managed identity, executes DataLakeServiceClient operations, and returns structured responses to the agent.

For standalone Microsoft Agent Framework without Azure AI Agents Service, you cannot use OpenAPI specifications at all. Instead, create function tools that directly wrap the SDK calls. The flow simplifies to: Agent Framework agent → Python function tool → azure-storage-file-datalake SDK → OneLake Lakehouse. This approach requires more manual coding but works with the open-source SDK and can run anywhere, not just in Azure.

## Missing architectural components identified

Your architecture specification omits several critical components needed for production implementation. The OpenAPI specification itself must be hosted somewhere accessible to the agent runtime. Options include inline in code (for development), Azure Blob Storage with public or SAS access, Azure API Management with automatic OpenAPI export, or source control repositories loaded at runtime.

The authentication token flow requires explicit design. Agents need tokens to call your wrapper API, and the wrapper needs tokens to call OneLake. For Azure AI Agents Service, use OpenApiManagedAuthDetails with the wrapper API audience. For the wrapper-to-OneLake connection, use DefaultAzureCredential to obtain storage-scoped tokens. The token audience for OneLake must always be `https://storage.azure.com/`.

Error handling and resilience patterns are missing from your architecture. Production systems need retry logic for transient failures, rate limiting to avoid OneLake throttling, input validation before SDK calls, and comprehensive logging for observability. The azure-storage-file-datalake SDK should be wrapped in retry decorators, and all operations should include timeout configurations.

Observability and monitoring require OpenTelemetry instrumentation, Application Insights integration for metrics and logs, and Azure AI Foundry's built-in evaluation tools for agent performance tracking. Without these components, debugging production issues becomes extremely difficult.

## Current best practices from official documentation

Microsoft's current guidance strongly recommends using Azure AI Agents Service rather than standalone Agent Framework when you need OpenAPI integration. The cloud service provides native specification parsing, automatic tool generation, managed authentication, and enterprise features including durability, observability, and content safety filters. Attempting to build OpenAPI support into standalone Agent Framework requires significant custom development.

Use endpoint-based authentication with `AIProjectClient(endpoint=..., credential=...)` rather than deprecated connection string methods. Microsoft removed connection string support from SDK versions above 1.0.0b10 and recommends migrating all hub-based projects to new Foundry project architecture. Connection strings are considered less secure than managed identity approaches.

Prefer workspace and lakehouse GUIDs over names for path construction. GUIDs are immutable identifiers that survive renames, deletions, and other workspace changes. Names can break integrations if administrators rename resources. The Fabric REST API returns GUIDs in workspace and lakehouse metadata responses.

Implement wrapper APIs rather than exposing OneLake directly through OpenAPI specifications. Wrappers provide input validation, business logic enforcement, structured error responses, and abstraction of underlying storage details. This pattern follows API gateway and facade design principles that improve security and maintainability.

Enable required Fabric admin settings before deploying to production. The "Allow service principals to use Power BI APIs" setting must be enabled for managed identity authentication. The "Users can access data stored in OneLake with apps external to Fabric" setting permits external SDK access. Both settings are found in the Fabric Admin Portal under tenant settings.

## Specific API references and corrections

**Incorrect:** `OpenAPITool.from_file()` does not exist in any Microsoft SDK.  
**Correct:** `OpenApiTool(name=..., spec=..., auth=...)` in Azure AI Agents Service (`azure-ai-agents` package).

**Incorrect:** `AIProjectClient.from_connection_string()` is the current API.  
**Correct:** `AIProjectClient(endpoint=..., credential=...)` is the modern, supported pattern.

**Correct as stated:** `AzureOpenAIResponsesClient` for Agent Framework integration with Azure OpenAI.

**Correct as stated:** `agent.run(tools=...)` pattern for tool calling at runtime.

**Correct as stated:** `azure-storage-file-datalake` SDK for OneLake access.

**Correct as stated:** `https://onelake.dfs.fabric.microsoft.com` endpoint.

**Correct as stated:** Workspace/lakehouse ID path construction.

**Correct as stated:** Managed Identity authentication support.

## Recommended architecture for production

Deploy this validated architecture for production systems: Create an Azure AI Foundry project with endpoint-based authentication using managed identity credentials. Use Azure AI Agents Service (not standalone Agent Framework) to enable native OpenAPI 3.0 tool support. Implement a custom wrapper API using Azure Functions or App Service that exposes lakehouse operations through an OpenAPI 3.0 specification with GET and POST endpoints.

The wrapper API uses the azure-storage-file-datalake SDK to interact with OneLake at `https://onelake.dfs.fabric.microsoft.com`. Authentication flows from the agent to wrapper API using managed identity tokens, and from wrapper to OneLake using storage-scoped tokens. All operations use workspace and lakehouse GUIDs for immutable path references.

Configure OpenAPI tool definitions with operationId fields for each lakehouse operation (ReadFile, ListFiles, etc.), JSON Schema parameter validation, and OpenApiManagedAuthDetails for secure authentication. The agent orchestrates tool calls based on user queries, the wrapper validates inputs and executes SDK operations, and structured responses flow back through the chain.

This architecture aligns with current Microsoft documentation as of October 2025, uses supported and non-deprecated APIs, provides enterprise-grade security through managed identities, and follows best practices for cloud-native agent systems. The approach separates concerns appropriately—agents handle orchestration, wrappers handle business logic, and SDKs handle storage operations—creating a maintainable and scalable solution.