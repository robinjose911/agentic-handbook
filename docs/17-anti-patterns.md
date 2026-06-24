# 17 · Anti-patterns

The fastest way to learn agent engineering is to recognize the failure shapes before you build them.
Each anti-pattern below names what it is, where it bites, and the specific fix. Most are the shadow of
a good idea applied past its range.

## 1. Multi-agent over-engineering

Splitting a tightly-dependent task across many agents because multi-agent sounds advanced. The
sub-agents make conflicting assumptions and produce incoherent output — the failure modes the
[Berkeley MAST taxonomy](../references.md#mast-taxonomy) catalogs are architectural, not prompt-level,
and [Cognition](../references.md#cognition-dont-build-multi-agents) showed this for dependent work.
**Fix:** single-agent for deep dependent work; reserve multi-agent for breadth-first, weakly-coupled
sub-tasks ([chapter 02](02-decision-framework.md)).

## 2. Framework lock-in

Adopting a heavyweight framework before you understand the patterns, then bending your system to its
abstractions. **Fix:** learn the patterns first ([chapter 03](03-pattern-catalog.md)); keep the agent
loop thin and the framework replaceable; score the decision with the
[build-vs-buy harness](../templates/build-vs-buy-harness.md).

## 3. Eval theater

A dashboard full of green that measures nothing the user cares about — vanity metrics, no golden set,
no gate. **Fix:** an [eval plan](../templates/eval-plan-template.md) with labeled cases, a real
threshold, and a regression gate on every change ([chapter 13](13-evaluations.md)).

## 4. The agent telephone game

Passing summaries between agents until the original intent is lost. Each handoff drops context.
**Fix:** explicit artifact handoff (structured outputs, not prose summaries) and a single owner of the
goal in orchestrator-worker designs.

## 5. Dashboard budgets

Putting the cost limit on a dashboard a human is supposed to watch. The $47,000 (illustrative —
verify) multi-agent loop ([chapter 11](11-security-and-threat-model.md)) ran unbounded because
nothing stopped it (_self-reported / illustrative_). **Fix:** a hard, pre-execution budget cap (USD/tokens/steps)
enforced before each step ([chapter 05](05-memory-state-and-durable-execution.md)).

## 6. MCP shadow IT

Engineers wiring up unvetted MCP servers because it is easy. Each is an injection and supply-chain
surface ([chapter 06](06-protocol-stack-skills-mcp-a2a.md)). **Fix:** an allowlist, pinned versions,
and signed updates via [MCP server governance](../templates/mcp-server-governance.md).

## 7. Service-account-with-everything

Giving the agent one credential that can do anything, "to keep things simple." The confused-deputy
blast radius is total. **Fix:** least-privilege, per-tool scoped tokens
([chapter 10](10-agent-identity-and-auth.md)).

## 8. Planning-only, execution-skipped

Generating an elaborate plan and never verifying the steps actually ran or succeeded. **Fix:**
planner-executor with a verification step and re-planning on failure
([chapter 03](03-pattern-catalog.md)).

## 9. Prompt-injection denial

Assuming "our users wouldn't do that," when the threat is untrusted *content* the agent reads, not the
user. **Fix:** run the [prompt-injection threat model](../templates/prompt-injection-threat-model.md);
break a leg of the lethal trifecta ([chapter 11](11-security-and-threat-model.md)).

## 10. Single-judge-LLM evaluation

Trusting one LLM judge with no code assertions and no human calibration. Judges have length, position,
and sycophancy bias and can be gamed. **Fix:** pair the judge with code-based assertions and calibrate
it against humans ([chapter 13](13-evaluations.md)).

## 11. Self-loop via the filesystem

An agent that writes a file it then re-reads as input, looping on its own output until it drifts or
burns budget. **Fix:** input-hash loop detection and a step cap
([chapter 05](05-memory-state-and-durable-execution.md)).

## 12. Chain-of-thought as truth

Treating the model's stated reasoning as a faithful account of what it did, and logging it as an audit
trail. The CoT can be post-hoc rationalization. **Fix:** audit the *actions* (tool calls, observations)
via traces ([chapter 14](14-observability-lite.md)), not the narration.

## 13. Vendor benchmark mimicry

Quoting a vendor's headline benchmark as if it predicts your production performance. A τ-bench number
without its scoring rule is noise ([chapter 13](13-evaluations.md)). **Fix:** run your own eval on your
own data; label any external figure _self-reported — verify_.

## 14. Multi-tool-call sprawl

Exposing dozens of overlapping tools so the model picks the wrong one or chains too many. **Fix:**
a small, sharp tool set with clear [contracts](../templates/tool-contract-template.md), and CodeAct
where many small steps compose better as code ([chapter 07](07-codeact-vs-tool-calls.md)).
