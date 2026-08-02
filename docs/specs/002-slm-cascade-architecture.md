---
status: proposed
date: 2026-08-02
---

# Fixed-domain SLM with LLM escalation: a cascade workflow pattern

## Background

A whitepaper ("Fixed-Domain Small Language Models with LLM Escalation") proposes a
three-layer architecture for client-specific agents: a small, domain-fine-tuned model
handles the bulk of requests, a lightweight trigger decides when its output can't be
trusted, and a general-purpose LLM handles the escalated remainder. The motivating
example is a Tender Comparison Agent (Copilot Studio + Azure Functions + PydanticAI +
Azure OpenAI), but the pattern is generic. This spec translates that architecture into
a concrete implementation on top of Agent Framework's existing workflow primitives,
as a sample plus a possible follow-on core contribution.

## What is the goal of this feature?

Give Agent Framework users a documented, runnable pattern for routing a request to a
cheap/fast agent first and escalating to a stronger agent only when validation fails,
using primitives that already exist in the framework (`WorkflowBuilder`,
`AgentExecutor`, `add_switch_case_edge_group`) rather than inventing new abstractions.

Value: users building high-volume, domain-narrow agents (tender comparison, clause
extraction, ticket triage, etc.) get a template that cuts LLM cost/latency for the
common case without sacrificing coverage on the long tail, and get an escalation log
for free as a byproduct — the same log the whitepaper needs for iterative fine-tuning.

Success metric: a runnable `getting_started` sample where the escalation rate on a
representative test set is a printed, trackable number — the same metric the
whitepaper calls out in its open questions ("what escalation rate is acceptable, and
how should it be monitored over time").

## What is the problem being solved?

Today there is no sanctioned example of tiered model routing in this repo. The closest
precedent, `python/samples/getting_started/workflows/control-flow/switch_case_edge_group.py`,
branches on a *classification label* (spam / not-spam / uncertain), not on *output
validity of the same task*. Two things are genuinely non-obvious and worth writing
down once instead of everyone re-deriving them:

1. `ChatResponse.try_parse_value()` (`agent_framework/_types.py`) silently swallows
   `pydantic.ValidationError` and just logs it — it does not raise or set an error
   flag on `AgentRunResponse`. Anyone building a validation-triggered escalation on
   `response_format` output needs to know to check `response.value is None` (or parse
   the schema themselves) rather than expect an exception or a `.success` field.
2. There's no framework-native confidence score or "reliability" signal on an agent
   response (no logprobs surface through `AgentRunResponse`, no built-in classifier
   hook). Escalation triggers have to be built from what's actually available:
   schema/parse failure, rule-based checks on the parsed fields, or a small separate
   judge/classifier agent — this should be documented explicitly so users don't go
   looking for something that isn't there.

## Architecture, mapped onto Agent Framework primitives

| Whitepaper layer | Framework primitive |
|---|---|
| Layer 1 — domain SLM | `AgentExecutor` wrapping a `ChatAgent` pointed at a small/fine-tuned model deployment (e.g. an Azure AI Foundry serverless or self-hosted endpoint), called with `response_format=<shared pydantic schema>` |
| Layer 2 — escalation trigger | A plain `@executor`-decorated function (or `Executor` subclass) sitting between the SLM node and the rest of the graph, wired via `WorkflowBuilder.add_switch_case_edge_group()` with `Case`/`Default` |
| Layer 3 — LLM fallback | A second `AgentExecutor` wrapping an Azure OpenAI-backed `ChatAgent`, using the **same** `response_format` schema |

```python
from pydantic import BaseModel
from agent_framework import AgentExecutor, WorkflowBuilder, Case, Default, executor

class TenderComparison(BaseModel):
    winning_vendor: str
    score: float
    rationale: str

slm_agent = AgentExecutor(slm_chat_agent, id="slm_compare")
llm_agent = AgentExecutor(llm_chat_agent, id="llm_compare_fallback")

@executor(id="escalation_check")
async def escalation_check(response: AgentExecutorResponse, ctx: WorkflowContext) -> None:
    try:
        result = TenderComparison.model_validate_json(response.agent_run_response.text)
    except ValidationError:
        await ctx.send_message(EscalationDecision(escalate=True, reason="schema_validation_failed"))
        return
    if result.score < 0 or result.score > 1:
        await ctx.send_message(EscalationDecision(escalate=True, reason="score_out_of_range"))
        return
    await ctx.send_message(EscalationDecision(escalate=False, result=result))

workflow = (
    WorkflowBuilder()
    .set_start_executor(slm_agent)
    .add_edge(slm_agent, escalation_check)
    .add_switch_case_edge_group(
        escalation_check,
        [
            Case(condition=lambda d: d.escalate, target=llm_agent),
            Default(target=finalize_result),
        ],
    )
    .build()
)
```

This deliberately does **not** invent a new `CascadeBuilder` abstraction up front —
`switch_case_edge_group` already expresses "branch on a predicate over the previous
node's output" exactly. Reusing it keeps the sample idiomatic and means anyone who
already knows `WorkflowBuilder` can read it without learning a new API.

### Shared output schema

Both agents are constructed with the same `response_format=TenderComparison`
(whitepaper §3, "Shared output schema"). This is what makes the switch-case swap
transparent to whatever calls the workflow — the caller reads a `TenderComparison`
regardless of which layer produced it.

### Full deferral vs. refinement (whitepaper §3)

Ship full deferral first (`llm_agent` gets the original input, not the SLM's partial
output) — it's what the sample above does, and it's the safer default the whitepaper
itself recommends. Note refinement (passing the SLM's partial output as a prompt seed
to the fallback agent) as a documented variant, not the default, since it risks
anchoring the fallback to the SLM's error.

### Escalation logging

Wrap the whole workflow invocation (or add an `AgentMiddleware` per ADR 0007,
`docs/decisions/0007-agent-filtering-middleware.md`) that, whenever the
`escalation_check` branch fires, appends a record — input, SLM output, escalation
reason, LLM output — to a log sink. This log is exactly the fine-tuning dataset the
whitepaper's §5 iteration strategy needs, and it comes for free from the workflow
structure rather than needing bespoke instrumentation. `AgentMiddleware.process()`'s
`context.result` gives a second, complementary interception point if teams want
logging decoupled from the graph itself (e.g. for telemetry export via
`ChatMiddleware`) rather than as an explicit node.

### RAG for volatile facts (whitepaper §3)

Out of scope for the routing sample itself, but call out explicitly in the sample's
README: if the task depends on current regulatory/policy knowledge, that's a
retrieval concern (a tool/function on either agent), not something the SLM should be
fine-tuned to memorize. Don't conflate "teach the SLM the comparison logic" with
"teach the SLM today's regulations."

## Deliverables

New sample under `python/samples/getting_started/workflows/cascade/`:

- `schema.py` — shared pydantic `response_format` model for the domain task.
- `agents.py` — constructs the SLM `ChatAgent` (parameterized endpoint, so it works
  against an Azure AI Foundry serverless deployment, a self-hosted vLLM/Ollama
  endpoint, or — for the sample to run without a fine-tuned model on hand — a second
  Azure OpenAI deployment standing in for "the small model") and the LLM fallback
  `ChatAgent` (Azure OpenAI).
- `workflow.py` — the `WorkflowBuilder` graph above, plus the `escalation_check`
  executor and a small `EscalationDecision` message type.
- `run_and_log.py` — batch-runs a CSV/JSONL of sample inputs, prints the escalation
  rate, and writes escalated cases to a JSONL log in the schema needed for future
  fine-tuning (whitepaper §5, step 2–4).
- `README.md` — explains the pattern, the two known gaps in §"What is the problem
  being solved" above, the deferral-vs-refinement tradeoff, and how to point the
  "SLM" agent at a real fine-tuned deployment once one exists.

No changes to `agent_framework` core are required to build this — it's composable
entirely from existing public API (`WorkflowBuilder`, `AgentExecutor`, `executor`,
`Case`/`Default`, `response_format`).

## Open questions

Carried over from the whitepaper, now scoped to what the sample can actually help
answer:

- What escalation rate is acceptable in production, and how should it be tracked
  over time? — the sample's `run_and_log.py` gives a way to *measure* this per run;
  deciding the acceptable threshold is a product decision per deployment, not
  something the framework should hardcode.
- Confidence mechanism: model-intrinsic (logprobs) vs. separately trained classifier?
  Framework today exposes neither on `AgentRunResponse` — if logprob-based confidence
  turns out to be commonly wanted, that's a separate, larger proposal (provider-level
  API surface change), out of scope here. The sample ships with schema/range
  validation only, and documents the classifier-agent option as a "bring your own"
  extension (a third `AgentExecutor` node whose output feeds `escalation_check`).
- Should a `CascadeBuilder`/`add_cascade_edge_group` convenience wrapper be added to
  core once this pattern is validated by real usage, the way `add_switch_case_edge_group`
  already exists? Recommend: not yet — ship as a sample, revisit if multiple teams
  independently hand-roll the same `escalation_check` shape.
- .NET parity: `dotnet/src/Microsoft.Agents.AI.Workflows` has the equivalent graph
  primitives (`SwitchBuilder`, `HandoffsWorkflowBuilder`) but no middleware type with
  parity to Python's `AgentMiddleware` yet. A .NET sample is straightforward to add
  once/if there's demand; not included in this first pass.

## E2E code sample

See the `WorkflowBuilder` snippet under "Architecture" above — that is the shape the
`workflow.py` deliverable will follow, extended with real `ChatAgent` construction and
the `run_and_log.py` batch driver.
