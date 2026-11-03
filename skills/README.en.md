# ObaPick Agent Skills

[日本語](README.md)

You can use these **small, reusable instructions for AI coding agents** without installing ObaPick's helper programs from `tools/`. Each skill lives in its own folder and includes a `SKILL.md` explaining what the AI should do and when to use it.

## Start with one skill

1. Download this repository using GitHub's **Code → Download ZIP**, or clone it.
2. Open `skills/` and select one folder for your current task, for example `obapick-find-code/`.
3. Copy **the entire selected folder** into the skill directory **inside your development project**. Do not mix different skills' files.
4. Ask your AI: “Use obapick-find-code to locate the settings-loading code and related tests.” If it does not appear, consult your agent's skill discovery and reload instructions.

| Coding agent | Project skill destination | Official guide |
| --- | --- | --- |
| Codex | `.agents/skills/obapick-find-code/SKILL.md` | [Codex skills](https://developers.openai.com/codex/skills) |
| Claude Code | `.claude/skills/obapick-find-code/SKILL.md` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| GitHub Copilot | `.github/skills/obapick-find-code/SKILL.md` | [Copilot skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |
| Gemini CLI | `.agents/skills/obapick-find-code/SKILL.md` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |

The `skills/` directory in ObaPick is the **distribution source**. Not every agent automatically discovers skills in that location. Check your agent's current project-skill settings.

### Copy via the terminal (optional)

From the ObaPick repository root, replace `../my-project` with the project where you use the AI. This example uses the shared Codex/Gemini directory; change the destination for Claude Code or Copilot according to the table above.

Linux/macOS:

```sh
mkdir -p ../my-project/.agents/skills
cp -R skills/obapick-find-code ../my-project/.agents/skills/
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "../my-project/.agents/skills"
Copy-Item -Recurse "skills/obapick-find-code" "../my-project/.agents/skills/"
```

Inspect existing files before overwriting a skill with the same name.

## Choose only what you need

| Task | Skill |
| --- | --- |
| Find relevant files and tests | [obapick-find-code](obapick-find-code/SKILL.md) |
| Make a focused code change | [obapick-small-change](obapick-small-change/SKILL.md) |
| Review changes and verification | [obapick-review-changes](obapick-review-changes/SKILL.md) |
| Pause and hand off work safely | [obapick-handoff](obapick-handoff/SKILL.md) |
| Write clear, actor-specific documentation | [obapick-clear-docs](obapick-clear-docs/SKILL.md) |
| Check Python changes | [obapick-python-check](obapick-python-check/SKILL.md) |
| Check Go changes | [obapick-go-check](obapick-go-check/SKILL.md) |
| Reduce a bug report to a reproducible failure | [bug-reproduction-brief](bug-reproduction-brief/SKILL.md) **(external OSS, original English text)** |

You do not need to install every skill. A skill is an instruction, **not an added tool permission**. Your agent still needs access to the files, commands and tests required for a task. Review its actual diff and results.

ObaPick-authored skills are covered by the repository's [MIT License](../LICENSE). For any redistributed third-party skill, see [LICENSES.en.md](LICENSES.en.md) for the publisher, original source, pinned revision, modification status, and copyright/license notices.
