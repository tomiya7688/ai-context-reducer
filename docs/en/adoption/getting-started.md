# Try a tool that helps choose what to give an AI

Japanese version: [AIに渡す資料を選ぶ道具を試す](../../jp/導入/AIに渡す資料を選ぶ道具を試す.md).

Before asking an AI to fix a bug, try showing a project overview and possible investigation methods. This guide covers downloading a helper tool and getting your first result. Allow about five minutes for a small project; download and scan times depend on your connection and project size.

## 1. Choose and extract a release archive

Open the [latest release page](https://github.com/tomiya7688/ai-context-reducer/releases/latest). The published v1.0.0 is the standard command-line release. Under “Assets,” choose the archive for your operating system and CPU. The “Source code” downloads do not provide the executables used below.

| Operating system | CPU type | v1.0.0 filename ending | Compressed size |
|---|---|---|---|
| Windows | x64 | `windows-x64.zip` | 5.1 MiB |
| Windows | arm64 | `windows-arm64.zip` | 4.7 MiB |
| Linux | x64 | `linux-x64.tar.gz` | 4.8 MiB |
| Linux | arm64 | `linux-arm64.tar.gz` | 4.4 MiB |
| macOS | x64 | `macos-x64.tar.gz` | 4.8 MiB |
| macOS | arm64 | `macos-arm64.tar.gz` | 4.5 MiB |

Sizes come from the attached files in [published v1.0.0](https://github.com/tomiya7688/ai-context-reducer/releases/tag/v1.0.0), converted to MiB (1,048,576 bytes) and rounded to one decimal place.

If you do not know your CPU type, check “System type” under “Settings → System → About” on Windows. On Linux or macOS, run `uname -m` in a terminal: choose x64 for `x86_64`, or arm64 for `aarch64` or `arm64`.

Extract the downloaded archive. The overview and suggestion commands below use the distributed executable, so you do not need to install a Python or Go runtime. Check the requirements separately if you choose another, more detailed analysis. You can also read the [v1.0.0 distribution validation record](../../../release/validation/v1.0.0.md).

## 2. Run commands from the extracted folder

Open a command prompt or terminal with the folder containing `acr-toolbox` as its working folder. On Windows, open that folder in File Explorer, type `cmd` in the address bar, and press Enter. On Linux or macOS, open a terminal and use `cd "/path/to/extracted/folder"` to enter it.

Replace the project paths below with the folder you want to inspect. Specify your project containing the code, rather than the folder containing the extracted tools.

Windows:

```text
.\acr-toolbox.exe analyze "C:\path\to\your-project"
.\acr-toolbox.exe select "C:\path\to\your-project"
```

Linux or macOS:

```text
./acr-toolbox analyze "/path/to/your-project"
./acr-toolbox select "/path/to/your-project"
```

`analyze` shows an overview, such as languages and file counts. `select` uses that overview to suggest investigation methods to try next. Neither command checks code correctness or automatically runs the suggested tests or analyses.

## 3. Look at actions related to your task

Results use JSON, a format that pairs field names with values. Start with these fields:

| Field | What to look for |
|---|---|
| `status` | `ok` means the scan succeeded. `ok_with_warnings` means some reads had problems; check whether needed files are missing. |
| `project_root` | Check that it inspected the project you specified. |
| `language_file_counts` | Check which source languages are present. |
| `recommended_tools` and `conditional_tools` | Lists of actions to try. Each item's `reason` explains the suggestion, `activation` describes when it applies, and `availability` describes availability conditions. |

For example, if you want to locate the code that saves settings, you can start with the search suggestion. You do not need to run unrelated documentation cleanup or analyses for other languages.

To try a search, run the following from the extracted folder. Replace `save` and the path ending in `src` with the name to find and your project's source folder.

Windows:

```text
.\acr-toolbox.exe search --max-results 20 "save" "C:\path\to\your-project\src"
```

Linux or macOS:

```text
./acr-toolbox search --max-results 20 "save" "/path/to/your-project/src"
```

Use result paths and line numbers to ask the AI to read the related code and tests. This reduces the unrelated file contents you provide. Ask it to check the located code and requirements rather than deciding the cause from search results alone.

## 4. Give the results to your AI

Paste or attach the task description and relevant overview and search results in the AI you normally use. Adapt this request to your task:

```text
Task: Fix a setting that resets after restarting the app.
Project folder: [project path]

Use the attached overview and search results to investigate the setting save code,
startup loading code, and related tests.
Read the relevant code and requirements, make the fix, and check that the saved
setting survives a restart.
If information is missing, search the additional locations needed.
At the end, report the changes, checks run and their results, and anything you could not verify.
```

If a chat-only AI cannot read your files, also attach the located code, requirements, and tests.

## If something goes wrong

- **The command is not found**: Set the folder containing `acr-toolbox.exe` or `acr-toolbox` in the extracted archive as your working folder.
- **The executable will not start**: Check that the archive matches your operating system and CPU. If the OS asks you to review a downloaded app, check the distributor and file before following the OS instructions.
- **`input_missing` or `input_not_directory`**: Check that the project folder exists at the specified path. Quote paths containing spaces, as in the examples.
- **`scan_failed` or `ok_with_warnings`**: Review the error or unreadable locations, and inspect files needed for this task another way.

## Where to go next

- [Find a method by the problem you have](../method-index.md) — Find ways to narrow information and example AI requests for your task.
- [Helper tool documentation](../../../tools/README.md) — Find other operations and the detailed tool guides.
