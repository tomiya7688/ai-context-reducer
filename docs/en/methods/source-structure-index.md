# Find functions and where they are used
> Japanese version: [関数や使われている場所を探す](../../jp/手法/関数や使われている場所を探す.md)


This example shows how to find the parts of a large program related to a change. The file and function names below are examples.

## Example: change what happens when a settings file is missing

Suppose a made-up settings app should use default settings when its settings file is missing. A list of code locations shows:

```text
Settings-loading code: load_settings
File containing it: src/settings.py
Place that uses it: app.py
File for checking its behavior: tests/test_settings.py
```

Give these locations to the AI and ask it to check:

1. Read `src/settings.py` to see what happens now when the settings file is missing.
2. Read `app.py` to see where the loaded settings are used.
3. Read `tests/test_settings.py` to see how the current behavior is checked and what to check after the change.

These three places give you enough to start planning the change. You do not need to read the settings screen or unrelated libraries first. If you discover another file is involved, check that file too.

## When to use this

This is useful when it takes a long time to find related parts in a large program. For a small task where you already know what to change and how to check it, ordinary file search is enough.

## Do not rely on the list alone

The list may be out of date or may not show every connection. Open the actual program and the files used to check its behavior, and confirm the list is correct. Do not decide the impact or safety of a change from the list alone.

## Tell the AI what to do

```text
Search for the name of the code I am changing. List where it is defined, where it is used, and which tests relate to it.
Open the listed code and related tests to confirm the list is current.
If you find a connection missing from the list, include that area and its tests.
```

## Why this reduces context

Give the AI the list and ask it to start from related code and the places that use it instead of opening every file to guess how they connect. The list is only a starting point; ask the AI to confirm the code and tests needed to make a decision.

## Terms

A function is a named operation that can be called from another part of a program.

## Optional helper tool

- If useful, the [Function and file relationship tool](../../../tools/common/large/source-structure-index/README.md) lists relationships between functions and files. Use it to find related code. Treat the list as a starting point and have the AI check the code and tests too.

Ordinary search or tools already used by the project can serve the same purpose.
