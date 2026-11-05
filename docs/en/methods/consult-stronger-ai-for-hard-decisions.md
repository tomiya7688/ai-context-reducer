# Ask another AI only for difficult decisions

> Japanese source of truth: [難しい判断だけ別のAIに相談する](../../jp/手法/難しい判断だけ別のAIに相談する.md)

Some coding steps are routine, but choosing a new storage architecture or deciding whether a failed approach should be abandoned can cause substantial rework if the wrong decision is made. This does not mean every step must run on the most expensive model.

This method keeps routine investigation, implementation, and testing with an **executor AI**, and consults an **advisor AI only at consequential decision points**. The advisor challenges assumptions, alternatives, missing evidence, and conditions under which the planned approach fails. The executor then checks the advice against original sources and test results instead of treating it as a guaranteed answer. [1][2]

**You** define the task, required conditions, permissions, and completion criteria. The executor decides when a permitted consultation is useful. The advisor provides criticism or a course correction, while the original code, specification, and tests provide the evidence. A different model does not automatically provide independent or correct conclusions.

This complements [Avoid unnecessary reasoning and repeated attempts](avoid-unnecessary-reasoning-and-retries.md). If you already have design options to compare, see [Compare proposed design options with project evidence](compare-design-options-with-project-evidence.md).

## 1. Divide the responsibilities

| Participant | Responsibility | Do not |
| --- | --- | --- |
| **You** | Set goals, constraints, permissions, when to consult, and completion criteria | Replace approval or tests with the fact that an advisor was consulted |
| **Executor AI** | Find originals, edit code, run checks, and consult when justified | Treat advice as unquestionable or declare success without evidence |
| **Advisor AI** | Challenge the chosen approach, identify counterexamples, missing evidence, and possible checks | Claim to have read inaccessible files or run tests it did not run |
| **Original sources and checks** | Establish current requirements, behavior, and test results | Be replaced by a model's opinion alone |

An advisor does not automatically make an edit safe. Changes to data formats or public APIs still require checking affected consumers and migration paths.

## 2. Decide when a consultation is warranted

Consulting on every decision makes another model reread material and may increase cost and latency. Use this sequence:

```text
Do you have the needed requirements, code, and test evidence?
  ├─ No → retrieve the relevant originals first
  └─ Yes
       ↓
Can the executor safely make and verify a routine decision?
  ├─ Yes → proceed and run necessary tests
  └─ No / potentially high impact
       ↓
Would another perspective help with a design fork, contradiction,
lack of progress, or completion risk?
  ├─ Yes → consult with the decision and evidence
  └─ No → obtain a measurement or ask the responsible human
       ↓
Check advice against original sources and tests
       ↓
Proceed with necessary approval, or stop
```

Potential triggers include conflicting specifications, architectural trade-offs affecting multiple modules, repeated failure without a new causal explanation, and a high-impact completion review. Consultation is usually unnecessary for a short, obvious edit, an action already dictated by a test result, or a question where relevant evidence has not yet been gathered. [1]

If the same command is retried without changing its inputs and fails identically, **stop the unproductive loop first**. Consult only when a new hypothesis or consequential choice would benefit from outside criticism. Obtain missing evidence before asking another model to speculate.

## 3. Example: choosing how to persist settings

Suppose a fictional application loses saved settings after restart. You require offline operation, preservation of existing data, and passing the relevant tests.

- **Investigate:** The executor examines current save/load code, data format, and tests, identifying the revision read.
- **Decision fork:** It considers repairing JSON persistence versus migrating to a database, and is unsure whether a migration is actually necessary for this bug.
- **Consult:** Provide the constraints, code/test source references, alternatives, and specific question. Ask the advisor to identify invalid approaches, migration risks, and evidence that would change the recommendation.
- **Verify:** If the advisor suggests checking whether saving and loading use the same location, the executor inspects those actual implementations and tests; the advice text is not a test result.
- **Finish:** Implement the justified change, run required checks, review the diff, and obtain appropriate human approval. Report unresolved constraints rather than claiming completion.

This is an **illustrative workflow**, not a measured result. For comparing already proposed options, follow the [design comparison method](compare-design-options-with-project-evidence.md).

## 4. Supply a specific decision and supporting evidence

The request should say **what to challenge and against which requirements**, not merely “think harder.”

| Supply | Example |
| --- | --- |
| Decision to make | Repair JSON or migrate to a database |
| Non-negotiable requirements | Offline operation, data preservation, no unapproved dependency |
| Evidence gathered | Current specification, implementation paths and revision, failing test and result |
| Executor's proposal and rationale | Keep JSON to avoid migration, but concurrent writes remain unverified |
| What to challenge | Failure modes, overlooked dependencies, alternative causes, evidence that changes the choice |
| Verification after advice | Save/restart/load test, compatibility with prior settings |

This targeted evidence handoff works when **you delegate to an independent AI or a separately configured subagent**. **Claude Code's built-in Advisor Tool works differently**: the advisor receives the complete transcript, including earlier tool calls and results, rather than only this selected evidence. [1][3]

### Request you send to the AI

```text
Task: [task].
Use the executor AI for routine investigation, edits, and tests.

When an important design fork, conflicting evidence, or stalled investigation
makes a decision difficult, consult an authorized advisor AI.
First identify the exact decision, required conditions, original source
locations and revisions, candidate approaches, weaknesses, and unknowns.

Ask the advisor for counterexamples, failure conditions, and missing evidence.
Verify any recommendation against current specifications, code, and tests.
Do not skip required approvals or safety and behavior checks.

Do not repeatedly consult for trivial edits or before the needed evidence exists.
Report consultation count, additional checks, actual validation, and gaps.
```

This instruction **cannot create a model-consultation feature** in an AI tool that does not support one. Without suitable access, ask the executor to organize the question and evidence for a separate chat or human reviewer.

## 5. Compare Advisor Tool with related methods

Claude Code's **Advisor Tool** lets its main model request advice from a second model at important decision points. Anthropic documents the `/advisor` command, the `advisorModel` setting, and the `--advisor` launch flag, with `/advisor off` to disable it. The feature is **experimental** and has model and platform restrictions; use the [current official guide][claude-code-advisor] for availability. [1]

| Method | When the higher-capability model runs | Context and limitations |
| --- | --- | --- |
| **Claude Code Advisor Tool** | Selected decision points chosen by the main model | Advisor reads the **full conversation and tool results**; Claude Code has no setting for a forced maximum consultation count |
| **Targeted review by another AI** | Decision points you specify | Can send selected relevant sources, but missing evidence can impair advice |
| **Planning-only stronger model (`opusplan`)** | Planning mode | Switches to a more economical model during execution rather than consulting mid-task |
| **Delegated subagent** | Throughout an independently delegated subtask | Must define task scope and evidence passed to the subagent |
| **Switching the main model** | Entire work after switching | Useful when sustained higher capability matters, but all that work runs at the selected model's cost |

An application using the Advisor Tool **directly through the Claude API** can configure controls such as `max_uses` in supported setups. Do not assume the same controls exist in Claude Code's `/advisor` interface. [3]

**Tree of Thoughts**, a separate research method, explicitly generates and evaluates branching candidate reasoning paths with search and possible backtracking. A consultation with a second model **does not imply that a Tree of Thoughts search took place**. These approaches have different mechanisms and costs. [4]

## 6. Context, cost, and quality

**Adding an advisor does not necessarily reduce context.** Claude Code's advisor reads the whole transcript, so consultations on long conversations can themselves be expensive. Anthropic states that toggling the Advisor Tool does not invalidate the executor's prompt cache, but **the advisor does not reuse its own transcript computation between consultations** in Claude Code. [1]

The **Claude API** offers advisor-side caching options in supported configurations. Do not assume those API options work in the same way in Claude Code's user interface. [3]

Compare **whole-task cost**, including executor input/output, advisor input/output, cache-related billing, tools or searches, and retries. Advisor calls add direct usage. They can be worthwhile when better early decisions prevent additional investigation, edits, or verification later.

In an April 2026 announcement, Anthropic reported that in **its own SWE-bench Multilingual evaluation**, Sonnet 4.6 with an Opus 4.6 advisor improved accuracy by 2.7 percentage points and lowered cost per agentic task by 11.9% compared with Sonnet 4.6 alone. The setups differed: the solo Sonnet used adaptive thinking, while the advised executor had thinking disabled. **Do not attribute the entire observed difference to the advisor alone or extrapolate it to other tasks.** [2]

### Measure the effect

Compare **executor alone**, **executor with selective consultation**, and **higher-capability model alone** on matching tasks and completion criteria. Record task revision, model/version, reasoning settings, tools, permissions, order, and preferably repeated attempts.

| Record | Why |
| --- | --- |
| Completion success, required tests, and remaining defects | Prevent a cheap but incorrect result from appearing successful |
| Cumulative input/output and cache components by model | Account for all executor and advisor work |
| Actual cost or an estimate with explicit rates | Avoid declaring savings merely because the executor model was cheaper |
| Number of consults and transcript length at those points | Identify excessive consultations and expensive repeated reads |
| Tool executions, retries, and elapsed time | Check whether the advice reduced rework or introduced delay |
| Missing evidence and conflicts with originals | Include cases where the advice made the task worse |

Do not add cache-read or internal reasoning component counts again when they are already included in input/output totals. Mark inaccessible usage as unmeasured, rather than guessing from visible final-answer length. See [Estimate context use by task](../ai-usage/estimate-context-use-by-task.md).

## 7. Avoid over-consulting

Consultations on simple tasks add cost and latency. If advice is inconclusive, first determine whether the decision needs more original evidence, a real measurement, or a human choice, rather than asking the same question again.

For permissions, private data, and external actions, check which information can be provided to a second model. Built-in Claude Code consultations receive the entire conversation, so **do not place information in that conversation that the advisor is not permitted to receive**. Independent advice never removes required approvals or tests.

For a simple change, finding the right original source and validating the change may be the best choice. Evaluate whether consultation improved **the burden of reaching a correct outcome**, rather than treating multiple models as an objective.

## References

**Checked November 5, 2026.** These are official documents, a vendor evaluation, and a research paper. The example and decision sequence above are illustrative and were not benchmarked by ObaPick.

1. **Anthropic**. [Claude Code: Escalate hard decisions with the advisor tool][claude-code-advisor] — activation, timing, complete transcript, cost/caching, limitations, and comparisons.
2. **Anthropic** (April 9, 2026). [The advisor strategy: Give agents an intelligence boost](https://claude.com/resources/articles/the-advisor-strategy) — provider evaluation, conditions, and results.
3. **Anthropic**. [Claude API: Advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) — server-side consultation, context, costs, and API controls.
4. **Shunyu Yao et al.** (2023). [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://proceedings.neurips.cc/paper_files/paper/2023/hash/271db9922b8d1f4dd7aaef84ed5ac703-Abstract.html) — deliberate exploration of branching reasoning paths, a separate method.

[claude-code-advisor]: https://code.claude.com/docs/en/advisor
