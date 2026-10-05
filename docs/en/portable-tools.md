# Use Tools with Fewer Additional Installs

> Japanese Source of Truth: [追加インストールを減らしてツールを使う](../jp/追加インストールを減らしてツールを使う.md)

Do not require users to install a new language environment or development kit just to use a helper tool. Choose from tools that are already available or distributed ready to use, and consider another environment only when those tools cannot perform the necessary check. This avoids preparing a large runtime or researching setup instructions for every task.

## Example: searching code without Python

Suppose an AI needs to find code on a user's Windows machine, but Python is not installed. If the task only needs text search, a distributed executable or an existing search command may be enough. The user can find relevant files without installing or configuring Python.

By contrast, checking types or whether a project builds may require a language runtime or development kit. A development kit is a set of tools for building and checking a program. If the required environment is missing, switch to another available check or say that the check could not be performed. Do not silently install software just to report a check as complete.

## Choose a suitable option

First decide how much checking the task needs, then choose from the available options. A search command or lightweight built-in feature may be enough for simple searches. Use existing language tools when you need project-wide dependency or build information. A small task does not need a large analysis environment.

Use an external tool if it is already available. If it is not, check whether a built-in or simpler option is sufficient. If no available method can verify a requirement, record it as unverified. Discuss installation only when an additional environment is truly necessary.

For this repository's tool-selection behavior, commands, file placement, and overwrite rules, see the [`language-setup`](../../tools/common/small/language-setup/README.md), [`materialize-tools`](../../tools/common/small/materialize-tools/README.md), and [`acr-toolbox`](../../tools/common/native/acr-toolbox/README.md) guides.

## Example request to the AI

> First check which search, analysis, and runtime tools are already available. Choose an option that needs no additional installation. Mark unverifiable requirements as unverified and report only available options and checks that could not be run.

## Optional tools and terminology

[language-setup](../../tools/common/small/language-setup/README.md) checks available analysis; [materialize-tools](../../tools/common/small/materialize-tools/README.md) places portable tools. This approach is called **Portable Tooling** or a no-install fallback. Avoiding installation alone does not reduce context; context is reduced only when the AI receives the needed results instead of irrelevant material.
