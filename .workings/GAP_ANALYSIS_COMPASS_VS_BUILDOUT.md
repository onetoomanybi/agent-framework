# GAP ANALYSIS: Compass Artifact vs BUILD_OUT_PROMPT.md
## October 18, 2025

---

## EXECUTIVE SUMMARY

The Compass artifact identifies **critical architectural issues** in the BUILD_OUT_PROMPT.md that the current build guide does NOT address. These are production-blocking issues that will cause implementation failures if not resolved during the build-out phases.

**Critical Findings:**
- **CRITICAL**: Product confusion between Microsoft Agent Framework (SDK) and Azure AI Agents Service (cloud service)
- **CRITICAL**: USE OF DEPRECATED APIs in current code (connection string, AIProjectClient patterns)
- **HIGH**: Missing wrapper API layer for OpenAPI integration
- **HIGH**: OpenAPI tool specification lacks required `operationId` fields
- **HIGH**: Authentication token flow is incomplete/incorrect
- **MEDIUM**: Fabric admin settings prerequisites not documented
- **MEDIUM**: Agent Framework integration patterns need clarification

**Impact**: Code in `.workings` folder will not work as-is when deployed to production. Build-out prompt assumes capabilities that don't exist or uses deprecated patterns.

---

## DETAILED GAP ANALYSIS

### 1. PRODUCT CONFUSION - MOST CRITICAL

#### What Compass Says
> "Native OpenAPI 3.0 support exists ONLY in Azure AI Agents Service (a cloud service within Azure AI Foundry), NOT in the standalone Microsoft Agent Framework SDK."

#### What BUILD_OUT_PROMPT Says
- Assumes OpenAPI specs can be loaded into agents
- References `openapi_spec.json` as the integration mechanism
- Doesn't specify which product is being used (Agent Framework vs AI Agents Service)
- Treats them as interchangeable

#### The Gap
**BUILD_OUT_PROMPT is ambiguous about which product is being used.**

Current code uses:
```python
from azure.ai.projects import AIProjectClient  # This is Azure AI Agents Service
client.agents.get_agent(agent_id)
client.agents.create_and_process_run(...)
```

But BUILD_OUT_PROMPT doesn't clarify:
- Is this standalone Agent Framework or Azure AI Agents Service?
- Which APIs actually exist in v1.0.0?
- If using Agent Framework, how is OpenAPI loaded?

**Reality**: The code IS using Azure AI Agents Service (via `azure-ai-projects` SDK), but BUILD_OUT_PROMPT doesn't make this explicit.

#### Impact on Build-Out
- Developer might try to use Agent Framework SDK instead
- Developer might expect OpenAPI tool loading that doesn't exist
- Developer will hit 400 Bad Request errors without understanding why

**Missing in BUILD_OUT_PROMPT**:
- [ ] Explicit statement: "This project uses Azure AI Agents Service, not standalone Agent Framework"
- [ ] Clarification of which `azure-ai-projects` SDK version supports which features
- [ ] Documentation that OpenAPI loading requires Azure AI Agents Service

---

### 2. DEPRECATED API USAGE - CRITICAL

#### What Compass Says
> "AIProjectClient.from_connection_string() is deprecated and no longer recommended. Use endpoint-based authentication with managed identities instead."

#### What Current Code Does
```python
client = AIProjectClient(endpoint=endpoint, credential=credential)  # ✓ This is correct
```

#### What BUILD_OUT_PROMPT Says
- Doesn't address deprecation
- Doesn't document authentication evolution
- Task 1.2 only says "verify methods exist" without checking for deprecation

#### The Gap
**BUILD_OUT_PROMPT doesn't include Task 1.2 validation for deprecated patterns.**

Current code actually DOES use the modern pattern (endpoint-based), but:
- The prompt doesn't explain WHY this is the only supported pattern
- Developer could introduce deprecated patterns when modifying
- No guidance on avoiding connection-string based code
- No mention of managed identity as the enforced authentication method

#### Impact on Build-Out
- During Phase 1 Task 1.2, developer might "verify" old patterns are acceptable
- If code needs updates, developer might revert to deprecated patterns
- Migration from hub-based projects not documented

**Missing in BUILD_OUT_PROMPT**:
- [ ] Task 1.2 should include: "Verify NO connection string usage exists"
- [ ] Documentation: "Only endpoint + DefaultAzureCredential pattern is supported"
- [ ] Migration guide from deprecated hub-based projects
- [ ] RBAC role requirements (Azure AI User, Cognitive Services OpenAI User, etc.)

---

### 3. MISSING WRAPPER API LAYER - HIGH PRIORITY

#### What Compass Says
> "Azure AI Agents Service requires a custom wrapper API that implements the OpenAPI specification. The agent calls this wrapper, which then uses azure-storage-file-datalake SDK to access OneLake."

#### Current Architecture Flow
```
Agent → API Endpoint (Function App) → Lakehouse SDK → OneLake
```

#### What's Missing
**The wrapper API does NOT exist in the architecture.**

Current `function_app.py` IS the wrapper, but:
- It's not documented as such in BUILD_OUT_PROMPT
- The relationship between OpenAPI spec and Flask routes is not explained
- Developer doesn't understand: "OpenAPI spec DESCRIBES this Function App"

#### The Gap
**BUILD_OUT_PROMPT doesn't explain the wrapper pattern.**

Current architecture assumes:
1. OpenAPI spec is defined (`openapi_spec.json` ✓)
2. Azure Function App implements the spec (`function_app.py` ✓)
3. But: How does Azure AI Agents Service KNOW about this spec?
4. But: How is the spec registered with the agent?
5. But: How does authentication flow work?

These critical questions are unanswered.

#### Impact on Build-Out
- Developer creates the OpenAPI spec and Function App
- But doesn't know how to register it with the agent in AI Foundry
- Doesn't know whether the spec should be:
  - Uploaded to AI Foundry UI?
  - Loaded from blob storage?
  - Embedded in code?
  - Served from the Function App itself?

**Missing in BUILD_OUT_PROMPT**:
- [ ] Diagram showing OpenAPI spec → AI Foundry → Function App flow
- [ ] Step-by-step: How to register OpenAPI spec in AI Foundry UI
- [ ] Where to host the OpenAPI spec (blob storage, inline, etc.)
- [ ] Task in Phase 1: "Verify wrapper API implements all OpenAPI operations"
- [ ] Task in Phase 3: "Register wrapper API with agent in AI Foundry"

---

### 4. OPERATIONID REQUIREMENT - HIGH PRIORITY

#### What Compass Says
> "Azure AI Agents Service requires the operationId field in EVERY OpenAPI operation. Although optional in OpenAPI 3.0 spec, it's REQUIRED for Azure AI Agents Service."

#### What openapi_spec.json Does
```json
"/listFiles": {
  "post": {
    "operationId": "listFiles",  // ✓ Present
    ...
  }
}
```

#### What BUILD_OUT_PROMPT Says
- Nothing about operationId requirement
- No validation that operationId is present in every operation
- No guidance on operationId naming (letters, hyphens, underscores only)

#### The Gap
**openapi_spec.json is CORRECT, but BUILD_OUT_PROMPT doesn't validate or explain why.**

If developer modifies the spec later:
- Might add operations without operationId
- Gets 400 Bad Request error without understanding why
- No error message explains the requirement

#### Impact on Build-Out
- Developer might remove or rename operationId values
- Might add operations from examples that lack operationId
- No validation step catches this error

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 1 Task: "Verify all OpenAPI operations have operationId field"
- [ ] Documentation: "operationId is REQUIRED by Azure AI Agents Service"
- [ ] Validation: Only letters, hyphens, underscores allowed
- [ ] Test: Attempt to create agent with missing operationId → expect 400 error

---

### 5. AUTHENTICATION TOKEN FLOW - INCOMPLETE

#### What Compass Says
> "Agents need tokens to call your wrapper API, and wrapper needs tokens to call OneLake. For Azure AI Agents Service, use OpenApiManagedAuthDetails. For wrapper-to-OneLake, use DefaultAzureCredential."

#### What Current Code Does
**Agent → Wrapper**: Not shown in current code (handled by AI Foundry framework)  
**Wrapper → OneLake**: Uses managed identity ✓

#### What BUILD_OUT_PROMPT Says
- Task 1.1 mentions token creation but doesn't explain flow
- No documentation of OpenApiManagedAuthDetails
- No guidance on Fabric admin settings prerequisites
- Doesn't explain token scopes required

#### The Gap
**BUILD_OUT_PROMPT doesn't document authentication prerequisites and flow.**

For production deployment:
1. Function App needs Managed Identity with RBAC in workspace
2. Fabric Admin Portal needs "Allow external apps to access OneLake" enabled
3. OpenAPI tool needs OpenApiManagedAuthDetails configuration
4. Token scopes must be exactly `https://storage.azure.com/`

Current BUILD_OUT_PROMPT doesn't address any of this.

#### Impact on Build-Out
- Deployment will fail: "Unauthorized to access OneLake"
- Developer doesn't know to enable Fabric admin settings
- Developer doesn't understand token scope requirements
- Wrapper API might use wrong credential method

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 1 checklist: "Enable Fabric admin settings for external app access"
- [ ] Phase 1 checklist: "Assign Managed Identity to workspace with Contributor role"
- [ ] Phase 4: Task "Configure OpenApiManagedAuthDetails for wrapper API"
- [ ] Documentation: Token scope MUST be `https://storage.azure.com/`
- [ ] Task: "Verify token flow from Agent → Wrapper → OneLake"

---

### 6. HTTP METHOD RESTRICTIONS - NOT DOCUMENTED

#### What Compass Says
> "Only GET and POST HTTP methods are supported. PUT, DELETE, PATCH operations are not available in Azure AI Agents Service OpenAPI tools."

#### What openapi_spec.json Uses
- All operations are POST ✓

#### What BUILD_OUT_PROMPT Says
- Nothing about method restrictions
- No validation of supported HTTP methods

#### The Gap
**If developer modifies OpenAPI spec, they might use unsupported methods.**

Current spec is compliant, but:
- Developer might add PUT for "update file" operation
- Might add DELETE for "remove file" operation
- No validation catches this at build time
- Gets 400 Bad Request at runtime without clear error

#### Impact on Build-Out
- Extensions to API might be broken
- Developer assumes REST conventions (POST=create, PUT=update, DELETE=remove)
- Reality: Only GET and POST work

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 4: Task "Document API method restrictions (only GET/POST supported)"
- [ ] Phase 5: Add to deployment guide: "Method limitation of Azure AI Agents Service"

---

### 7. FABRIC ADMIN SETTINGS PREREQUISITES - CRITICAL FOR DEPLOYMENT

#### What Compass Says
> "Enable 'Users can access data stored in OneLake with apps external to Fabric' in Fabric Admin Portal. Enable 'Allow service principals to use Power BI APIs' for managed identity authentication."

#### What BUILD_OUT_PROMPT Says
- Nothing about Fabric admin portal
- No prerequisite checklist before deployment
- Configuration examples don't include Fabric settings

#### The Gap
**BUILD_OUT_PROMPT skips deployment prerequisites entirely.**

Current code assumes these settings are already enabled:
```python
client = DataLakeServiceClient(
    account_name="onelake",
    file_system_name=workspace_id,
    ...
)
```

But if settings aren't enabled:
- 403 Forbidden: "User does not have permissions"
- No clear error message about which setting to enable
- Developer confused about where to fix it

#### Impact on Build-Out
- Phase 5 deployment will fail silently
- Developer doesn't know why permission is denied
- Might spend hours debugging
- No rollback/troubleshooting guidance

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 5: "Pre-deployment Checklist" section with Fabric Admin Portal steps
- [ ] Step-by-step: How to enable each Fabric admin setting
- [ ] Troubleshooting: "If 403 Forbidden, check Fabric admin settings"
- [ ] Screenshots or guidance for Fabric Admin Portal navigation

---

### 8. AGENT FRAMEWORK vs AGENTS SERVICE CLARITY - MEDIUM

#### What Compass Says
> "Microsoft recommends using Azure AI Agents Service rather than standalone Agent Framework when you need OpenAPI integration. Standalone Agent Framework lacks native OpenAPI support."

#### What Current Code Uses
- `from azure.ai.projects import AIProjectClient` → Azure AI Agents Service ✓
- Not standalone Agent Framework

#### What BUILD_OUT_PROMPT Says
- References "Microsoft Agent Framework" generally
- Doesn't distinguish between two products
- Samples directory has many Agent Framework examples
- Confusing which approach to use

#### The Gap
**BUILD_OUT_PROMPT uses correct product but doesn't explain why.**

Build guide says:
> "The project consists of three main components working together:
> 1. Fabric Notebook Client
> 2. Agent Tool Implementation - Backend tools running in Azure AI Foundry
> 3. Azure Function App"

But doesn't clarify:
- Is this Agent Framework or AI Agents Service?
- Why not use standalone Agent Framework?
- When would you use each?

#### Impact on Build-Out
- Developer might try to import wrong libraries
- Might look at examples that don't apply
- During Phase 1 Task 1.2, might verify wrong SDK methods
- During Phase 3, might implement agent testing incorrectly

**Missing in BUILD_OUT_PROMPT**:
- [ ] Executive summary: "This project uses Azure AI Agents Service (not standalone Agent Framework)"
- [ ] Explanation: Why AI Agents Service is required for OpenAPI support
- [ ] Phase 1 Task 1.2: Verify methods from `azure-ai-projects` package
- [ ] Phase 3: Agent testing uses Azure AI Agents Service patterns

---

### 9. OPENAPI SPECIFICATION HOSTING - NOT ADDRESSED

#### What Compass Says
> "The OpenAPI specification itself must be hosted somewhere accessible to the agent runtime. Options include inline in code, Azure Blob Storage with SAS access, API Management, or source control."

#### What Current Project Has
- `openapi_spec.json` exists in `.workings` folder ✓
- But: Where is it deployed?

#### What BUILD_OUT_PROMPT Says
- Nothing about hosting the spec
- Doesn't explain how spec gets to AI Foundry agent
- No Phase 5 deployment step for spec

#### The Gap
**BUILD_OUT_PROMPT doesn't address spec hosting strategy.**

Deployment flow is unclear:
1. Developer creates spec ✓
2. Developer creates Function App ✓
3. Developer creates agent in AI Foundry... but how does agent get the spec?
4. Upload spec to blob storage? ✓
5. Upload spec to AI Foundry UI? ?
6. Host spec from Function App itself? ?
7. Serve from GitHub? ?

No guidance on this critical step.

#### Impact on Build-Out
- Phase 5 deployment is incomplete
- Developer must figure out spec hosting independently
- Might choose wrong hosting strategy (no security, no versioning, etc.)
- Multiple spec copies in different places (manual sync nightmare)

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 5 Task: "Decide spec hosting strategy (blob storage recommended)"
- [ ] Phase 5 Task: "Deploy spec to chosen hosting location"
- [ ] Phase 5 Task: "Register spec URL with agent in AI Foundry"
- [ ] Decision table: Pros/cons of each hosting option

---

### 10. ERROR HANDLING AND RESILIENCE - NOT DOCUMENTED

#### What Compass Says
> "Production systems need retry logic for transient failures, rate limiting to avoid OneLake throttling, input validation, and comprehensive logging."

#### What Current Code Does
```python
try:
    # One-shot operation, no retries
    ...
except Exception as e:
    print(f"Error: {e}")  # Basic error handling
```

#### What BUILD_OUT_PROMPT Says
- Phase 4 mentions "comprehensive logging"
- No mention of retry logic
- No mention of rate limiting
- No mention of timeout configurations

#### The Gap
**BUILD_OUT_PROMPT doesn't address production resilience patterns.**

Current code will fail on transient network errors:
- OneLake is temporarily unavailable → Operation fails
- Network timeout → Operation fails
- Rate limiting from OneLake → Operation fails

No retry logic to handle these.

#### Impact on Build-Out
- Phase 4 Code Quality passes tests
- But production deployment fails on first transient error
- No exponential backoff
- No circuit breaker
- No dead letter queue

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 4 Task: "Add retry decorators to all SDK calls"
- [ ] Phase 4 Task: "Configure timeout values (recommend 30-60 sec)"
- [ ] Phase 4 Task: "Implement rate limiting for large file operations"
- [ ] Phase 5: "Add Application Insights integration for monitoring"

---

### 11. OBSERVABILITY AND MONITORING - MINIMAL

#### What Compass Says
> "Without OpenTelemetry instrumentation, Application Insights integration, and Azure AI Foundry evaluation tools, debugging production issues becomes extremely difficult."

#### What BUILD_OUT_PROMPT Says
- Phase 4 mentions "comprehensive logging"
- No mention of OpenTelemetry
- No mention of Application Insights
- No mention of traces/spans
- No mention of AI Foundry evaluation tools

#### The Gap
**BUILD_OUT_PROMPT doesn't address production observability.**

Logging alone isn't enough:
- No distributed tracing across layers
- No metrics/instrumentation
- No performance visibility
- No AI evaluation of agent quality

#### Impact on Build-Out
- Phase 5 deployment will lack observability
- Production issues will be hard to debug
- Can't track performance bottlenecks
- Can't evaluate agent decision quality

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 5 Task: "Set up OpenTelemetry instrumentation"
- [ ] Phase 5 Task: "Configure Application Insights"
- [ ] Phase 5 Task: "Configure Azure AI Foundry evaluation metrics"
- [ ] Phase 5: "Add distributed tracing across Function App and OneLake calls"

---

### 12. RESOURCE PATH CONSTRUCTION CLARITY - MEDIUM

#### What Compass Says
> "Prefer workspace and lakehouse GUIDs over names. GUIDs are immutable and survive renames. Names break integrations if administrators rename resources."

#### What Current Code Does
```python
# Accepts workspace_id and lakehouse_id (could be either GUIDs or names)
# No validation of format
# No documentation of preference
```

#### What BUILD_OUT_PROMPT Says
- Doesn't address name vs GUID
- Config example doesn't show GUID format
- No guidance on where to get GUIDs
- No validation that GUIDs are used

#### The Gap
**BUILD_OUT_PROMPT doesn't enforce GUID usage.**

Current code will work with names or GUIDs, but:
- Names are brittle (break on rename)
- No documentation that GUIDs are better
- Developer might use names by default
- Configuration examples don't show GUID format

#### Impact on Build-Out
- Developer might use workspace/lakehouse names
- System breaks if administrator renames resources
- No warning about this fragility
- Production incident if rename happens

**Missing in BUILD_OUT_PROMPT**:
- [ ] Phase 1: Task "Validate configuration uses workspace/lakehouse GUIDs (not names)"
- [ ] Configuration guide: How to find GUIDs in Fabric UI
- [ ] Documentation: Why GUIDs are mandatory for production
- [ ] Phase 3 testing: Test with both GUIDs and names, note which works

---

## SUMMARY TABLE: GAP SEVERITY

| Gap | Severity | Current Impact | Phase | Action |
|-----|----------|-----------------|-------|--------|
| Product confusion (Agent Framework vs Services) | CRITICAL | Deployment fails | Phase 1 | Add Task 1.0 to clarify product choice |
| Deprecated API usage | CRITICAL | Future breaks | Phase 1 | Add Task 1.2.5 to check deprecation |
| Missing wrapper API documentation | HIGH | Developer confused | Phase 1 | Add architecture diagram |
| operationId requirement | HIGH | 400 errors | Phase 1 | Add validation to Task 1.4 |
| Authentication token flow | HIGH | 403 unauthorized | Phase 1 | Add Task 1.5 for token flow |
| Fabric admin settings | CRITICAL | Deployment fails | Phase 5 | Add pre-deployment checklist |
| HTTP method restrictions | MEDIUM | Future breaks | Phase 4 | Document in API design guide |
| Agent Framework vs Services clarity | MEDIUM | Developer confusion | Executive | Clarify in summary |
| OpenAPI spec hosting | HIGH | Deployment incomplete | Phase 5 | Add Task 5.0 for spec hosting |
| Error handling/resilience | HIGH | Production incidents | Phase 4 | Add Task 4.5 for retry logic |
| Observability/monitoring | HIGH | Production debugging hard | Phase 5 | Add Task 5.4 for OpenTelemetry |
| Resource path GUID vs name | MEDIUM | Brittleness | Phase 3 | Add validation to testing |

---

## RECOMMENDATIONS FOR BUILD_OUT_PROMPT UPDATES

### Immediate (Critical - blocks deployment):

1. **Add Phase 0 (Pre-Build Checklist)**:
   - Verify using Azure AI Agents Service (not standalone framework)
   - Enable Fabric admin settings
   - Verify Managed Identity in workspace
   - Confirm correct SDK versions

2. **Expand Phase 1 Task 1.2**:
   - Add check for deprecated patterns
   - Add RBAC role requirements
   - Add token scope validation (`https://storage.azure.com/`)

3. **Add Phase 1 Task 1.5**:
   - Authentication token flow diagram
   - OpenApiManagedAuthDetails documentation
   - Integration test of token propagation

### High Priority (Functional issues):

4. **Add Phase 5 Task 5.0**:
   - Decide OpenAPI spec hosting strategy
   - Deploy spec to blob storage
   - Register spec URL with AI Foundry agent

5. **Add Phase 4 Task 4.5**:
   - Add retry logic decorators
   - Configure timeouts
   - Implement rate limiting

6. **Expand Phase 3**:
   - Document agent testing with Azure AI Agents Service (not Agent Framework)
   - Show how to use OpenAPI specs in testing

### Medium Priority (Production readiness):

7. **Add Phase 5 Task 5.4**:
   - OpenTelemetry instrumentation
   - Application Insights integration
   - AI Foundry evaluation setup

8. **Add documentation**:
   - Architecture diagram showing wrapper pattern
   - Why GUIDs are mandatory (not names)
   - When to use each HTTP method

---

## CONCLUSION

**BUILD_OUT_PROMPT.md is 75% correct** and covers the basic build steps well. However, it has **critical gaps** in:

1. **Architectural clarity** (product confusion, wrapper pattern not explicit)
2. **Deployment prerequisites** (Fabric admin settings, authentication flow)
3. **Production readiness** (resilience, observability, error handling)
4. **API integration details** (operationId requirement, spec hosting, method restrictions)

**The code in `.workings` folder will NOT work in production without addressing these gaps.**

Recommended approach:
- Keep BUILD_OUT_PROMPT as-is for Phase 1-4 build steps
- Add Phase 0 (pre-build checklist) for prerequisites
- Add Phase 5 tasks for deployment and observability
- Add architecture documentation to explain wrapper pattern
- Add troubleshooting guide for common deployment failures

