# Avoid unnecessary reasoning and repeated attempts

> Japanese source: [AIに無駄な推論と再試行をさせない](../../jp/手法/AIに無駄な推論と再試行をさせない.md)

When you ask an AI to change code, it can spend too long considering alternatives to a straightforward edit, or run the same failing command repeatedly. The goal is **not to remove useful reasoning or verification, but to stop repetitions that no longer improve the result**.

You can decide what evidence is needed, how hard the task is, and when the AI should report a lack of progress. Whether you can directly control a model's reasoning effort depends on the product and model.

This guide covers **choosing reasoning effort, stopping when there is enough evidence, and preventing unproductive retries**. For stopping file investigation specifically, see [Decide when the AI should stop investigating](exploration-control.md). For inspecting previous runs, see [Diagnose repeated context from work logs](diagnose-repeated-context-from-work-logs.md).

## Understand what is being repeated

**Reasoning** is how an AI model uses its inputs to decide on an answer or next action. Some providers report how many tokens the model used for internal reasoning. **The length of the visible answer is not the same as the amount of internal reasoning.**

A **coding agent** combines a model with file search, editing, command execution and other tools. Therefore, two different problems need different remedies.

| Problem | Example | What you can try |
| --- | --- | --- |
| More model reasoning than the task needs | Comparing many designs for a one-line change | Choose a suitable reasoning-effort setting; specify scope and completion conditions |
| Repeated agent actions without progress | Running a command again with the same inputs and receiving the same error | Check what changed since the previous attempt; stop if there is no new evidence |

You may not have access to the model's full internal reasoning. You can often inspect tool calls, diffs and test results, but **do not claim those logs prove the model thought the same thing twice**.

## Method 1: Match reasoning effort to task difficulty

If your model or service offers a reasoning-effort setting, choose it according to the work and its consequences.

| Task | Starting point | When to increase effort |
| --- | --- | --- |
| Finding candidate files, sorting short texts, simple formatting | Lower effort | Requirements are ambiguous or results are unreliable |
| Small change in known code | Low to medium | The change affects other features or tests fail |
| Debugging, comparing architectural options | Medium to high | Causes are unclear, requirements conflict, or decisions are consequential |
| Authentication, data-loss risks, broad changes | Prioritize correctness and verification | Cutting reasoning or checks would create risk |

These are **starting considerations**, not universal settings or guarantees.

The [OpenAI API](https://developers.openai.com/api/docs/guides/reasoning) offers `reasoning.effort` for supported models. The [Claude API](https://platform.claude.com/docs/en/build-with-claude/effort) offers `effort` on supported models. Available settings, defaults and controls vary. **Writing “reason less” in a prompt does not reliably change hidden reasoning settings** if your coding agent does not expose a control.

For model selection and what your agent is allowed to read or execute, see the [AI usage FAQ](../ai-usage/faq.md).

### A budget for the whole task is different

Per-response effort and a budget spanning investigation, edits, checks and reporting are separate controls.

[Claude API task budgets (beta)](https://platform.claude.com/docs/en/build-with-claude/task-budgets) let you supply an **advisory token budget** for the entire agentic loop on select supported models. They include model thinking, tool calls, tool results and output. **This is not a strictly enforced cap and is not available through the normal Claude Code interface.** Check official support for your own environment; it is not a universal agent feature.

## Method 2: Stop deliberating after the necessary evidence and checks

Before work starts, define what the AI needs to know to make the change and what results will demonstrate completion.

For example, to fix settings that disappear after restarting an application:

1. Have the AI identify the save/load code, requirements and related tests.
2. Have it verify how to reproduce the issue and what existing behavior must remain unchanged.
3. Have it make the edit and run **tests for saving, restarting and loading settings**.
4. Inspect the diff and test results yourself, and finish when the conditions are met.

Once the required evidence and checks are satisfactory, do not add unnecessary tasks such as “compare five more designs” or “restate the same justification again.”

However, **failed tests, missing evidence, unclear downstream effects or missing authorization** are reasons to investigate further or report a blocker, not reasons to claim success.

## Method 3: Detect repeated attempts without progress

When an action fails repeatedly, have the AI examine **what changed since last time**, rather than merely telling it to try again.

The following example is fictional:

| Agent action | Observation | Next step |
| --- | --- | --- |
| 1. Run a test | Configuration file not found | Check the path and why it is missing |
| 2. Rerun without changing the file, command or environment | Same error | No progress: check the difference from the last attempt and pause |
| 3. Correct the path and retry | Different result | Inspect the new result and continue if needed |

**Two calls to the same command are not automatically waste.** Reproducing an intermittent error, checking non-deterministic behavior, or rerunning tests after an edit may be necessary. Compare the input, code revision, environment, result and purpose, not just the command text.

When an agent makes no progress, ask it to choose among these actions:

- Inspect one specific new source that could answer the remaining question.
- Change the identified cause, then test again.
- If information or permission is missing, report it and stop rather than guess or bypass restrictions.

You may set a retry limit, but it should depend on the task. Never skip needed tests or change permissions merely to make a failed run disappear.

## Method 4: Avoid duplicated self-checks but keep necessary tests

Requiring the AI to “make three plans, rerun every test, and then self-evaluate again” on every edit may consume additional time and tokens without improving quality.

A [2026 Microsoft Research study](https://www.microsoft.com/en-us/research/publication/agent-skills-can-be-harmful-an-empirical-study-of-skill-induced-failures-in-llm-agents/) investigated **307 skill-induced failures or efficiency regressions**, including **67 cases involving excessive verification**. These are cases in that study, **not a claim that 67% of ordinary AI work is wasteful**.

Instead, ask the AI to identify which areas the change can affect and run tests that actually verify those areas. **Keep necessary tests; remove only repetition that adds no new evidence.** See [Check a change in a way that matches what changed](validation-routing.md).

## Example message for you to send to the AI

Adapt this request for your project.

~~~text
Goal: Fix saved settings disappearing after restarting the app.

First identify the save/load code, relevant requirements and existing tests.
Verify how to reproduce the problem and which existing behaviors must not change.
Then make the necessary edit and run the tests needed for completion.
Report the actual diff and check results.

Once the known evidence is sufficient, do not repeat the same investigation
or comparison of options without a new reason.
If identical inputs and environment keep producing the same error,
first report what changed and what new evidence was found.

If there is no progress and no new evidence to inspect, pause.
Report what you tried, what remains unknown, and what information is needed.
Do not skip necessary tests or safety checks.
~~~

**This prompt does not enforce a hard internal-reasoning token limit.** Verify the agent's actual actions and required checks yourself.

## What the research actually demonstrates

Researchers sometimes call excessively long or repetitive model reasoning **overthinking**. Their methods differ in how they estimate difficulty and decide when to stop.

| Study | Proposed method | Reported findings and limits |
| --- | --- | --- |
| **[TALE (2025)](https://aclanthology.org/2025.findings-acl.1274/)** | Allocate a reasoning-token budget according to problem difficulty | Reduced reasoning token use in the evaluated settings, with a slight performance reduction reported |
| **[REFRAIN (2026)](https://aclanthology.org/2026.acl-long.1256/)** | Detect redundant reflection during reasoning and stop adaptively | Reduced tokens by 20–55% across four benchmarks and two model families while maintaining or improving accuracy versus standard reasoning |
| **[Sonata (2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/96dd7b14cde7e0a5194eceedafb2f249-Abstract-Conference.html)** | Use internal model representations to predict needed reasoning effort | Reduced thinking tokens by 20–60% under evaluated model and benchmark conditions while maintaining accuracy in those comparisons |
| **[ASAG (2026)](https://proceedings.mlr.press/v306/li26ev.html)** | Use internal attention information to judge whether more reasoning helps | About 40% fewer generated tokens with improved average accuracy in the reported Qwen3-8B evaluation |

**None of these numbers is a measured savings rate for ObaPick or coding agents in general.**

In particular, Sonata depends on internal model representations and ASAG on attention information. REFRAIN also needs a way to assess and end reasoning during generation. **You generally cannot turn these research algorithms on merely by writing a prompt in Codex or Claude Code.** Hosted services may not expose internal reasoning traces or model-state controls.

The practical lesson from TALE is to avoid excessive budgets for simple work. From research on early stopping, it is to reconsider whether more reasoning helps once the decision is supported. For an ordinary coding agent, start with **effort settings, explicit completion criteria and observable tool results**.

## Measure whether this helps

Compare comparable tasks under consistent conditions:

| Record | Why it matters |
| --- | --- |
| Goal, code revision, model and settings | Distinguishes the effect of a changed setting from a changed task |
| Required test results, completed edit, retries and manual intervention | Detects regressions despite lower token consumption |
| Input/output tokens and reasoning tokens if available | Measures consumption; record missing values as unmeasured |
| Command runs, repeated failures and task duration | Measures observable agent behavior separately from internal reasoning |

If reasoning tokens are included in an output-token total, do **not** count them again. The same applies to cached-input breakdowns. For accounting details, see [Estimate context use by task](../ai-usage/estimate-context-use-by-task.md).

**Reducing required evidence or skipping needed tests does not count as success.** If failures, unjustified early stops or repeated work increase, reconsider the effort setting or stopping criteria.

## References

- Han et al. (2025). [Token-Budget-Aware LLM Reasoning (TALE)](https://aclanthology.org/2025.findings-acl.1274/)
- Sun et al. (2026). [Stop When Enough (REFRAIN)](https://aclanthology.org/2026.acl-long.1256/)
- Li et al. (2026). [Adaptive Thinking (Sonata)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/96dd7b14cde7e0a5194eceedafb2f249-Abstract-Conference.html)
- Li et al. (2026). [Stop When Further Reasoning Won't Help (ASAG)](https://proceedings.mlr.press/v306/li26ev.html)
- Dong et al. (2026). [Agent Skills Can Be Harmful](https://www.microsoft.com/en-us/research/publication/agent-skills-can-be-harmful-an-empirical-study-of-skill-induced-failures-in-llm-agents/)
- [OpenAI API reasoning effort](https://developers.openai.com/api/docs/guides/reasoning)
- [Claude API effort](https://platform.claude.com/docs/en/build-with-claude/effort) and [task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets)
