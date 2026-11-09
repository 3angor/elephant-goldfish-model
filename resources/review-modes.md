# Review execution modes

This contract governs `egm-review`, `egm-review-loop`, `egm-resolve`, and their
reviewer delegation. It overrides conflicting EGM workflow defaults, never host
permissions or the user's latest instructions. It does not install software,
start bootstrap, or authorize unrelated project work.

## Inputs and precedence

- `ReviewMode`: `critique` (default) or `full`. This is independent of `Step`
  (stage selection) and the synthesizer's `Mode: REVIEW | BRAINSTORM`.
- `EditScope`: explicit files or bounded task the user authorized changing.
  In `full`, a request to correct the target document covers that document only;
  reviewing an implementation plan does not authorize implementing the product.
- `Checks`: agreed checks and their scope. Inspect commands before execution;
  never infer permission for installation, network access, or unsafe commands.
- `MaxRounds`: 2 review passes per selected stage by default, including re-audits.
- `MaxAgentLaunches`: 24 total launches per top-level run by default, including
  synthesizers, failed attempts, retries, duplicate reviewers, and descendants.
- `MaxParallelAgents`: 3 live child agents across the run by default, including
  synthesizers and descendants, further limited by the host's available slots.

Require positive integer budgets. Invalid configuration stops before dispatch.
The caller may lower limits. Raising limits requires an explicit user decision;
never silently reset counters on stage changes, nested calls, or resume. Print
mode, scope, and budget before starting. If mode is absent, use `critique` even
for `Step: uninterrupted`. An ambiguous "proceed" does not switch modes.

## Critique: analysis without target changes

Read the target and authorized context. Reviewers identify weaknesses, evidence,
alternatives, and trade-offs. Do not edit the target, code, configuration, or
project instructions. Do not invoke bootstrap, formatters, installers, or tests
with side effects. The only permitted writes are review/report artifacts in the
agreed output directory; never overwrite the target or unrelated existing work.
Where supported, constrain reviewer tools to read-only and reserve report writes
for the coordinator. A persona instruction is not a technical sandbox: disclose
when the host cannot enforce tool restrictions.

Run the selected review stages once. Return findings and alternatives, with
coverage and missing reviewers, then stop. Do not invoke the resolver's edit
path or offer auto-accept as an implicit continuation of this mode. A later
explicit request to fix findings starts `full` with a defined scope and budget.

## Full: bounded corrections and verification

1. Establish authorization for `EditScope` before the first change. If missing,
   ask one concrete scope question; until answered, only critique is allowed.
2. Review the current target with fresh, read-only reviewers. The coordinator
   alone applies justified fixes within the authorized scope. Preserve unrelated
   edits. Full mode is not blanket authority to alter architecture, security
   controls, credentials, dependencies, or data.
3. Escalate consequential design trade-offs, disputed findings, and changes
   outside scope. Leave them open; continue independent in-scope fixes if safe.
4. Run the agreed permitted checks after changes. Record each as passed, failed,
   blocked, or not run, with the actual command/result. A changed document may
   need structure/link checks, not application tests; a code fix needs relevant
   tests. Missing checks cannot be reported as passed.
5. Re-read the changed target and use a fresh independent reviewer for the
   affected scope before calling a fix verified. All launches and rechecks
   consume the same budgets. If no budget remains, report `fixed, unverified`.
6. Continue within budget without requiring approval for each already-authorized
   ordinary fix. Stop for scope changes, required confirmations, churn, exhausted
   budget, or missing essential inputs. Never merge, enable auto-merge, publish a
   release, or deploy to PROD as part of either review mode. Such actions require
   a separate user request and the host's applicable confirmation policy.

## Findings and stopping

Track stable finding IDs, severity, evidence, proposed alternative/fix, affected
scope, disposition, checks, and re-review result. `CONTEST` is a proposal with
checkable evidence, not an automatic dismissal. Keep disputed and residual
findings open unless the user explicitly accepts that specific trade-off or
independent evidence resolves it. Record who accepted a risk and why.

A cap, elapsed time, skipped fix, "continue", or agent silence never means risk
acceptance. Never automatically record residual findings as accepted trade-offs.
Do not label a report `resolved` merely because the resolution phase finished.
Use `critique complete`, `verified`, `open findings`, `budget exhausted`, or
`incomplete verification` as appropriate; report accepted risks separately.
A failed/missing reviewer is `not run`, not a clean review. Retry at most once
and only within remaining budget. Any reintroduced issue is reopened.

The coordinator owns a shared launch ledger. Prefer flat dispatch; reserve
specific launch/parallel slots before delegating to a synthesizer. Children may
not invent a fresh budget or launch unallocated descendants. If concurrency
cannot be tracked safely, dispatch sequentially. At exhaustion, write completed
coverage, skipped work, remaining findings, and a resumable summary, then stop.
These limits bound work; they do not guarantee a token or monetary ceiling.

## Examples

```text
egm-review TargetFile=design.md ReviewMode=critique Step=uninterrupted
MaxAgentLaunches=12 MaxParallelAgents=2
```

```text
egm-review TargetFile=design.md ReviewMode=full Step=uninterrupted
EditScope=design.md Checks="Markdown structure and local links"
MaxRounds=2 MaxAgentLaunches=24 MaxParallelAgents=3
```

These are skill inputs, not a new CLI executable or installed security boundary.
