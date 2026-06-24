# 16 · Production readiness

"Ready" is not a feeling, and it is not a demo that worked twice. It is a defensible answer to a
specific set of questions, asked by someone whose name goes on the launch. This chapter is the
narrative behind the go/no-go decision — the reasoning a CPTO walks through at each gate, and the
questions that separate "we think it works" from "we can operate this." The artifact you sign is the
[production-readiness checklist](../templates/production-readiness-checklist.md); this chapter is why
each gate is on it. The checklist gives you the boxes; the prose gives you the judgement to know when
a checked box is lying.

One framing discipline runs through every gate: the launch decision is a logical **AND**. Nine gates
that pass and one that fails is a no-go, not a passing grade. A waiver is not a pass — it is named, dated debt
with an owner, and a launch carried on three waivers is a launch you will be explaining in a
postmortem.

## Security, privacy, and the trifecta

Security is the gate most likely to be hand-waved and the one most likely to end your week. The first
question is not "is it secure?" but the
[lethal-trifecta](../references.md#willison-lethal-trifecta) question: does any single agent surface
combine access to private data, exposure to untrusted input, and the ability to communicate
externally? If all three meet on one path, a poisoned web page or a malicious email can turn your
agent into an exfiltration tool, and no prompt fixes it. Readiness means a leg is provably broken — by
architecture, not by hope. The [threat model](11-security-and-threat-model.md) must be current,
written against this specific agent, not a generic template, and tool credentials must be
least-privilege and scoped, never a shared god-token that turns one compromised tool into full account
access. Every write, spend, or send tool sits behind an approval gate; if the agent can move money or
data without a human in the loop, you are betting the company on a token predictor's good judgement.

Privacy is the quieter gate, and the one regulators ask about after the fact. The question is: what
can this agent read, and do you know? Inventory the data in context, minimize it — most PII in a
prompt is there by accident, not by need — and confirm payloads are logged by reference, not raw
([chapter 14](14-observability-lite.md)). "What is our retention and deletion policy for traces?" is a
question you want to have answered before a data-subject request forces it, not during.

## Cost, reliability, and rollback

Cost readiness is brutal and simple: is there a hard per-task cost cap enforced *before* execution,
not an alert that fires after a runaway loop has already burned the budget? An agent without a
pre-execution budget cap, step cap, and wall-clock cap is an unbounded liability, because the failure
mode of an agent is not "stops" — it is "loops forever, paying per token." Tie this to a dashboarded
[cost-per-task SLO](../templates/agent-slo-definition.md) and confirm the ROI hypothesis still holds at
the real expected volume, not the pilot's.

Reliability asks whether the agent survives the world being hostile. Are side-effecting tools
idempotent, so a retry does not double-charge a customer or send a duplicate email? Are there timeouts
and circuit breakers on every external call, and a defined graceful degradation for each failure mode?
"What happens when the model API is down?" should have an answer that is not "the agent hangs."

Rollback is the gate teams skip because nothing has gone wrong yet. The question is unforgiving: can
you get back to the last known-good version in one tested command, and does that rollback corrupt
in-flight state? A kill switch must halt the agent mid-flight, the operators authorized to pull it
must be named in advance, and — critically — the path must be rehearsed. A kill switch you have never
pulled is a hope, not a control. This gate is the precondition for the
[escalation runbook](../templates/escalation-runbook.md) meaning anything: the runbook tells on-call
*what* to do, but only if the rollback and halt it depends on actually exist and have been tested.

## Monitoring, evals, incidents, and compliance

Monitoring readiness closes the observability loop. Are lifecycle traces emitted for every run, with
dashboards for success rate, latency, tool errors, escalation rate, and cost, and alerts wired to
on-call at thresholds tied to the SLOs? The sharp question is about drift: "how would we know if the
agent got worse?" If the only answer is "a customer complains," you are not monitoring — you are
waiting.

Evaluations are the gate that proves quality is a number, not an anecdote
([chapter 13](13-evaluations.md)). Is there a labeled golden dataset, a launch-gate metric passing
*with margin*, and do evals run automatically on every change so a regression blocks the merge? If an
LLM-as-judge is in the loop, has the judge itself been validated, with its failure modes written down?
A judge you trust blindly is just a second unvalidated model in your release path.

Incident readiness asks whether you can respond without improvising. The
[escalation runbook](../templates/escalation-runbook.md) must exist, on-call must be staffed, severity
levels and comms templates defined, and the audit log must be immutable and sufficient to reconstruct
any single decision. "If the agent did something harmful at 2am, could we explain exactly what and
why by morning?" is the test.

The last gate is compliance, and the central message of
[chapter 12](12-eu-ai-act-as-architecture.md) is that you cannot bolt it on here. The agent's
capability tier carries an [EU AI Act](../references.md#eu-ai-act) risk class. If the system is
high-risk, the technical documentation (Art. 11), automatic logging (Art. 12), and human oversight
(Art. 14) must already be wired into the architecture — the same traces, approval gates, and audit
logs the other gates built. A team that designed for the trifecta, logged by reference, gated its
side effects, and kept an immutable audit trail has *already done* most of the compliance work; a
team that treats this gate as paperwork at the end discovers the architecture cannot produce the
evidence the regulation demands. Readiness is not nine independent checks — it is one coherent system
where security, observability, and compliance turn out to be the same controls viewed from different
gates. Sign the [checklist](../templates/production-readiness-checklist.md) when that coherence is
real, and not before.
