# Basic Guide

> Japanese Source of Truth: [基本方針](../jp/基本方針.md)

This repository describes ways to choose the information an AI needs for software development work. As a project grows, it is more efficient to locate the parts related to a request before reading them than to reread everything for every task.

The goal is not simply to make the AI read less. It is to reach the necessary information quickly and complete the work accurately by checking the original material.

## Example: fix an input field

Suppose an input field lets users submit an empty value. The relevant areas are the code that receives the value, the screen, the behavior after submission, and the tests for that behavior. There is no need to read unrelated screens or features in the project.

First clarify the request and how completion will be checked. Then use a file list or search results to narrow the candidates, and read the relevant implementation and tests. After making the change, choose a check suited to the input field and report any areas that could not be verified.

```text
confirm the request and completion criteria
  -> find the related implementation and tests
  -> read and change the original code
  -> verify with a check suited to the change
  -> report any unverified areas
```

A candidate list or short description helps locate where to read. When judging what code does or whether a change is safe, return to the original code and tests instead of relying on the list alone.

## Keep different kinds of information separate

Record project-wide rules, the project structure, and the current request with its completion criteria in the places meant for them. Copying the same instructions into every request makes them longer and risks leaving outdated details behind.

Keep detailed specifications in the document or implementation that owns them instead of repeating them in overview pages. Link short summaries and lists back to the original explanation.

## Match verification to the change

Choose checks based on what changed. Run related tests for a calculation change, check the screen when changing its behavior, and inspect the actual package when changing a release artifact.

State the scope of each check. Do not report “no issues” if a command did not inspect the target or if some areas could not be scanned.

## Add only the structure that helps

A small project may need only a short procedure and search. Add a list or automation when the project has grown and the same searches or checks are repeated. Avoid systems whose setup and maintenance take more effort than the repeated work they save.

When multiple people or AIs update the same project, check for changes made by others during your work. This helps avoid conflicts and prevents missing recent changes.

The [method index](method-index.md) explains specific methods and when to use them. [Adoption priority](adoption-priority.md) gives guidance on where to start.
