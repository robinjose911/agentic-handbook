# 08 · Computer-use & browser agents

Computer-use is the agent capability that makes executives lean in and security teams lean back. The
pitch is irresistible: an agent that sees a screen, moves a cursor, types, and clicks — automating any
software with a UI, no API required. The reality is that you are pointing a probabilistic system at the
single least-constrained action space in computing, and every page it loads is attacker-controlled
input. Both things are true. This chapter is about holding them at once: what these agents can do
today, where they fail, and the oversight without which you should not ship one.

## The landscape, as it stands

Two architectures dominate. **Computer-use agents** operate the whole desktop: they take screenshots,
reason over pixels, and emit raw mouse and keyboard events. **Browser agents** are scoped to a browser
and often work over the DOM and accessibility tree rather than pixels, which makes them faster, cheaper,
and more reliable for web tasks — at the cost of not touching native apps.

The frontier numbers, all vendor-reported and all worth treating as ceilings rather than expectations:

- **Anthropic Computer Use** (Claude Sonnet 4.5) reports roughly **61.4% on OSWorld** _(self-reported —
  verify)_, the standard real-computer-tasks benchmark — strong, and still far from the human bar.
- **OpenAI's Computer-Using Agent / ChatGPT agent** reports ~**68.9% on BrowseComp** _(self-reported —
  verify)_, a hard web-browsing benchmark.
- **Google's Gemini** ships a built-in computer-use capability in the same vein.
- **[Browser Use](../references.md#browser-use)** is the leading open framework for DOM-level browser
  agents; it **raised $17M in March 2025** _(self-reported, as of June 2026 — verify before relying)_
  and is the pragmatic on-ramp for teams who want a browser agent without building the harness.

The takeaway for a CPTO is not the leaderboard. It is that *the best system in the world still fails a
third or more of realistic computer tasks*. You are deploying a capable but unreliable operator, and
your architecture has to assume failure is routine, not exceptional.

## Where they break

**Anti-bot and environment friction.** Production websites do not want to be driven by robots. CAPTCHAs,
device fingerprinting, rate limits, bot-detection heuristics, and stealth measures are an adversarial
wall that breaks agents constantly. Treat "the agent got stuck on a Cloudflare challenge" as a baseline
operating condition. Building elaborate stealth to defeat these defenses also drags you into terms-of-
service and legal territory you should clear deliberately, not stumble into.

**Brittleness to UI drift.** A repositioned button, an A/B-tested layout, a new modal, a slow-loading
element — any of these derails a run that worked yesterday. Pixel-level agents are most exposed;
DOM-level agents degrade more gracefully but still break. Long horizons compound the problem: a
ten-step flow with 90% per-step reliability (illustrative) completes about a third of the time.

**Prompt injection from page content — the central security problem.** A computer-use agent reads the
page and acts on what it reads, which means *any text on any page it visits is untrusted instruction
input*. A hidden div, a planted review, a malicious email body can tell the agent to exfiltrate data,
make a purchase, or click a destructive link — and a naive agent will comply. This is the
[lethal trifecta](../references.md#willison-lethal-trifecta): the moment an agent combines access to
private data, exposure to untrusted content, and the ability to communicate externally, it is one
crafted page away from being turned against you. Browser agents sit *exactly* at that intersection by
design — they read the open web (untrusted content), often carry your session and credentials (private
data), and can navigate and submit forms (exfiltration channel). The full attacker model and the
mitigations live in [chapter 11](11-security-and-threat-model.md); the rule here is simpler: never give
a browser agent standing access to a privileged account it does not need for the current task, and
never assume page content is safe to act on.

**Silent wrong-doing.** The worst failures are not crashes — they are confident, plausible, wrong
actions. The agent "books the flight" on the wrong date, "pays the invoice" to the wrong vendor,
"submits the form" with hallucinated values. Because the action looks successful, nothing alarms unless
you instrumented for it.

## Oversight is the product

Given all of the above, the governing design principle is that *autonomy is earned per action class,
not granted to the agent wholesale*. Concretely:

**Run in watch-mode first.** New computer-use deployments should run with a human watching the live
session — every click visible, the human able to intervene — until you have real evidence of
reliability on your tasks. This is not a demo nicety; it is how you discover the injection and
drift failures before they cost you. Graduate to lower-touch oversight only on the strength of logged
runs, and graduate per task type, not all at once.

**Gate consequential actions with human-in-the-loop.** Reads and navigation can be autonomous; anything
that spends money, sends a message, changes a record, or crosses a trust boundary should hit an
approval checkpoint. Which actions require a human, who can approve, and the fallback when no one does
belong in a written policy — see the [human-in-the-loop policy template](../templates/human-in-the-loop-policy.md)
and adapt it before, not after, launch. The point of the policy is to make "the agent can click
anything" false by construction.

**Constrain the environment.** Run the agent in an isolated browser profile or VM with no ambient
credentials, scoped network egress, a per-session timeout, and a hard cap on the number and value of
actions. Inject credentials narrowly and just-in-time for the specific task rather than leaving the
agent logged into everything. A constrained environment turns a successful injection from a breach into
a contained, logged incident.

**Instrument for silent failure.** Log every action with a screenshot or DOM snapshot, assert
post-conditions where you can ("an order confirmation number now exists"), and alert on anomalies —
unexpected domains, value thresholds, action-rate spikes. You cannot supervise what you cannot see, and
the dangerous failures are precisely the ones that look like success.

Computer-use is genuinely transformative for the long tail of software that will never have an API. But
it is a power tool with the safety guard removed: deploy it watch-mode-first, gate every consequential
action, isolate the environment, and treat every page as hostile. Do that and it earns its place. Skip
it and you have built a confused deputy with your credentials and a browser.
