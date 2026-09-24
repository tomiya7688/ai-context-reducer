# Remote Context / Remote Delta First

> Japanese Source of Truth: [リモートとの差分を先に確認する](../jp/リモートとの差分を先に確認する.md)

When multiple AIs, chats, or developers update the same repository, the local state at the beginning of a task may no longer be current.

Instead of rereading the entire repository before implementation, first obtain a small summary of the delta from the remote.

## Basic flow

```text
local HEAD
   +
remote HEAD
   +
merge base
   ↓
remote commits
changed files
diff stat
bounded diff excerpt
   ↓
read only changes relevant to the current task
```

The important point is not to begin with a full diff or the full contents of every changed file.

First inspect a compact remote context containing items such as:

- local / remote identifiers
- ahead / behind state
- remote commit subjects
- changed file names / status
- diff stat
- a bounded diff excerpt

Expand to a full diff or target files only when this is insufficient.

## Bounded diff

Put an explicit limit on the diff excerpt.

The purpose is not a complete review. It is to understand cheaply where changes occurred and whether they affect the current task.

Make truncation explicit and keep a path back to the original diff when more evidence is needed.

## Safe update

If automation updates the local repository from the remote, avoid destructive automatic conflict handling.

Recommended rules:

- do not auto-update a dirty worktree
- do not auto-update when local commits have not reached the remote
- allow fast-forward only
- return conflicts / divergence to a human or explicit decision

Do not mutate repository state merely to reduce context.

## Read changed files selectively

Even after reviewing the remote context, you do not need to read every changed file.

Prioritize changed files relevant to the current task and add only the direct dependencies that are needed.

```text
remote delta
  -> relevant changed files
  -> direct dependencies
  -> full diff / additional docs only when needed
```

## Standardization level

### Standard recommendation

- make it possible to detect remote divergence at task start
- use a compact remote summary before a full diff
- keep diff excerpts bounded
- restrict automated updates to fast-forward
- stop on dirty or diverged state

### Optional implementations

- a helper that runs `git fetch`
- automatic display of remote commits / changed files / stat / excerpt
- a safe fast-forward option
- automatic insertion of remote context into a Context Pack

Git, GitHub, a specific OS, or a specific AI is not a required part of the method.
