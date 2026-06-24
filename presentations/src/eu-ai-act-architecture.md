# EU AI Act as Architecture — board one-pager

Read the EU AI Act as architecture, not paperwork. Three articles describe components you build into
the system — or bolt on expensively later. Build them in.

## The three articles as components

- Article 11 — Technical documentation. A living agent design spec + the capability-tier entry,
  generated from the system, not written about it after the fact.
- Article 12 — Record-keeping / traceability. An immutable audit log and lifecycle traces; every
  decision, tool call, and approval reconstructable.
- Article 14 — Human oversight. A human-in-the-loop policy and a kill switch wired into the loop — not
  a person told to keep an eye on it.

## Risk classes

The Act classifies by use case and context: minimal, limited, high-risk, prohibited. Map each agent's
capability tier to the risk class it floors at (see the capability-tier ladder one-pager). A sensitive
domain raises the floor regardless of autonomy.

## What it buys you

Designing to Articles 11/12/14 from day one yields an agent that is auditable, stoppable, and
documented — exactly what a board wants before sign-off and what the production-readiness checklist
demands. The EU lens is not overhead; it is the same discipline that makes security and evaluation
trustworthy, in a form a regulator recognizes.

## The differentiator

US-centric playbooks skip this. A European CPTO cannot. Treating compliance as architecture is how you
ship agents in regulated markets without a last-minute scramble — and how you turn "can we even do
this?" into a one-page answer.

This is an architectural aid, not legal advice. Confirm classification against current EU AI Act
guidance for your specific use case (as of June 2026 — verify before relying).
