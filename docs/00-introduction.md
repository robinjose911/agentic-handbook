# 00 · Introduction

> Production agents fail because the system *around* the model is weak. This handbook is about that
> system — the seven surfaces that decide whether an agent survives contact with production.

![The agent-vs-workflow decision tree](../assets/diagrams/00-hero-decision-tree.png)

## Who this is for

You are a CPTO, a staff engineer, or a founder deciding whether — and how — to put an agent in front
of real users, real money, or real data. You have read the launch threads and the framework READMEs.
What you are missing is the **decision discipline**: when an agent is the wrong tool, what to put
around it when it is the right one, and how to prove to a board (or a regulator) that it is safe.

This is a vendor-neutral playbook. It names patterns, anti-patterns, and the procurement-grade
artifacts a board can sign. It carries an explicit **EU AI Act** lens that US-centric playbooks skip
([see chapter 12](12-eu-ai-act-as-architecture.md)).

## The seven surfaces: AGENTIC

A reliable agent system has seven surfaces. They spell **AGENTIC**:

- **A**utonomy — how much the agent decides for itself, and where the workflow rails are.
- **G**oals — design specs and structured outputs that pin down what the agent is *for*.
- **E**valuation — the eval-driven loop and the observability that *proves* it works.
- **N**etworks — the protocol stack connecting agents to tools and to each other (Skills/MCP/A2A).
- **T**rust — security, the threat model, the EU AI Act, and the anti-patterns that get you breached.
- **I**dentity — who the agent is, what it may do, and how it authenticates.
- **C**ost — the cost stack and model selection that keep the bill survivable.

Each surface maps to specific chapters. The full map is in
[chapter 01](01-mnemonic-and-systems-map.md).

## How the repo is organized

- **[The guide](.)** — 19 chapters, this one first. Read the AGENTIC map, then the
  [decision framework](02-decision-framework.md) and [pattern catalog](03-pattern-catalog.md).
- **[Templates](../templates/README.md)** — 16 copy-paste, procurement-grade artifacts.
- **[Diagrams](../assets/diagrams/README.md)** — 15 Mermaid diagrams, sources included.
- **[Examples](../examples/README.md)** — five runnable mini-codebases that execute against a mock
  provider, with the trace and eval receipts committed.

## A ten-minute reading path

1. This page — the seven surfaces.
2. [Chapter 02 — Decision framework](02-decision-framework.md): do you even need an agent?
3. [Chapter 11 — Security](11-security-and-threat-model.md): the lethal trifecta and the Rule of Two.
4. [The capability-tier ladder](../templates/capability-tier-ladder.md): L0–L4 and the EU risk classes.
5. [One example run](../examples/README.md): watch an agent execute with the receipts.

## What this is not

This is **not** a framework — it takes no dependency you must adopt, and it argues that most "agents"
should be [workflows](02-decision-framework.md). It is **not** a tutorial series — it teaches
decisions, not keystrokes. And it is **not** a link list — every external claim sits in
[`references.md`](../references.md), and every reference earns its row. Where this handbook quotes a
volatile figure — a benchmark score, a star count, a CVE — that figure is labeled _as of June 2026 —
verify before relying_, because the field moves under your feet.
