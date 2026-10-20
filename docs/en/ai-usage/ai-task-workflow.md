# Shared AI workflow: From startup to pull request

> Japanese Source of Truth: [AIの作業開始からPRまでの共通ワークフロー](../../jp/AI利用/AIの作業開始からPRまでの共通ワークフロー.md)

This workflow prevents Claude Code, Codex, ChatGPT, and GitHub Copilot from starting work against stale repository state. The canonical rules are in the root [AGENTS.md](../../../AGENTS.md); this guide explains the sequence and when to stop.

**Rule: When an AI has access to a local Git checkout, it must successfully run `git pull --ff-only origin main` on `main` before substantive code investigation or editing.** Create a new task branch from the updated main. An environment without Git access must never claim that it ran git pull.

## 1. Check safety, then pull before starting work

The first operations are checking the worktree and synchronizing it. Do not start investigating a solution, changing files, or implementing an Issue first.

The standard procedure below assumes the shared remote is `origin` and work branches start from `main`.

~~~bash
# Check location, local changes, branch, and remote without modifying source.
git rev-parse --show-toplevel
git status --short
git branch --show-current
git remote -v

# Continue only when the worktree is clean and switching to main is safe.
git switch main
git pull --ff-only origin main
git rev-parse HEAD

# Only after a successful pull, start a task branch.
git switch -c docs/issue-number-short-description
~~~

The first four commands are **safety prechecks** before the required pull, not permission to skip it. If `git status --short` shows uncommitted or untracked work, identify its owner and stop until it can be handled safely. Do not forcibly switch branches.

`git pull --ff-only` fetches changes and only advances the local history if fast-forwarding is possible; it will not quietly create a merge commit when local history has diverged. Record the successful synchronization and resulting commit SHA.

**Stop if pull fails.** Report network/authentication issues, remote or branch mismatch, dirty worktrees, or diverged histories. Do not run `git stash`, `git reset --hard`, `git clean`, `git rebase`, automatic conflict-solving merges, or force pushes without explicit authorization. Never discard another contributor's work to make a pull succeed.

## 2. Existing task branches, worktrees, and environments without local Git

Distinguish a new task from continuing work on a branch.

| Environment | Required startup step | Limits |
| --- | --- | --- |
| **New work in a normal Git checkout** | Switch to a clean main and run `git pull --ff-only origin main`; branch from the updated main | No editing before synchronization |
| **Continuing an existing branch** | Check status, current branch, and upstream; run `git pull --ff-only` for that tracked branch if safe. Then check updated main with `git fetch origin main` | Inspect how main changes should be integrated; never silently merge or rebase |
| **Git worktrees with main in another worktree** | Inspect `git worktree list` and synchronize in the worktree that owns main, or use a separate safe worktree based on current remote main | Do not forcibly switch another worktree or remove its changes |
| **CI checkout or detached HEAD** | Verify the commit selected by the environment; fetch recent main when supported | Do not change the checkout under test just to make a pull work |
| **ChatGPT GitHub connector or other API-only environment** | Re-read the latest remote main SHA, the task branch, and the base commit; compare before editing or opening the PR | Fetching a SHA through the API is **not** executing git pull |

An existing branch may have no tracking branch for `git pull`; inspect and report this rather than guessing an upstream or merging unrelated histories. Respect explicitly chosen working branches.

Normal GitHub Actions checks use `actions/checkout` to test a particular commit. **Do not make CI pull main indiscriminately**, because that could change which commit the check tests. This workflow's mandatory pull applies to development agents with an editable local checkout.

## 3. Choose the Issue and scope from the updated state

After synchronization, review the requested Issue or PR and related changes, so completed work is not duplicated. Clarify the goal, permitted edits, completion criteria, and authoritative sources.

Do not load the entire repository by default. Narrow candidates using paths and searches, then inspect the required original code, specification, and tests. See [Context Priority](../context-priority.md).

For simultaneous agents, assign ownership and separate workspaces; see [Agent Edit Ownership](../methods/assign-agent-edit-ownership.md).

## 4. Make scoped changes and verify them

Keep the diff focused. Do not silently add dependencies or unrelated features. When modifying Japanese documentation, also update its English translation, `docs/DOCUMENT_MAP.json`, and affected indexes or links.

For documentation changes, run when available:

~~~bash
python3 .github/scripts/test_validate_documentation.py
python3 .github/scripts/validate_documentation.py .
~~~

For code changes, choose the relevant tests and static checks. Distinguish a passed check from a failed, skipped, or out-of-scope check. Do not overwrite another contributor's work if main changes during your task.

## 5. Before a PR, inspect the diff and the latest main

Before committing or opening a PR, inspect the changed files, diff, and recent remote main.

~~~bash
git status --short
git diff --check
git diff --stat
git fetch origin main
git log --oneline --left-right HEAD...origin/main
~~~

`git diff` without arguments does not include changes already committed; also inspect `git diff origin/main...HEAD` when appropriate. An initially successful pull does not guarantee main has stayed unchanged. Check integration options explicitly; do not silently rewrite history or force-push.

The PR should identify the Issue, purpose, reasons for the change, tests and results, and unresolved points. Check GitHub Actions and state whether the PR is still unmerged.

## 6. Hand off to the next AI or chat

Do not accumulate unrelated tasks in one conversation. Hand over the goal, starting SHA, current branch, modified files, completion criteria, verification results, unresolved work, and PR link. Link to large logs and sources rather than copying full histories.

**The next agent starts again with the synchronization and safety checks; it must not merely trust a handoff claiming that the repository was up to date.** See [Separate AI roles and chats by task](split-chats-by-task.md).

## Example startup request

~~~text
Follow AGENTS.md and the shared task workflow.
Before substantive code investigation or editing, check Git status and
run git pull --ff-only origin main on a safe, clean main checkout.
Report the resulting commit SHA before inspecting the Issue and sources.
If local changes, failed pull, or conflicts prevent syncing, stop and
report them instead of silently discarding or overwriting work.
If Git commands are unavailable, explicitly state that and verify
the latest remote SHA and task base. Do not claim to have run git pull.
~~~

## Sources

- [Git: git-pull](https://git-scm.com/docs/git-pull) — fetching and integration, including fast-forward-only mode.
- [Git: git-worktree](https://git-scm.com/docs/git-worktree) — handling multiple working trees.
- [GitHub: About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) — collaboration through diffs and merges.
