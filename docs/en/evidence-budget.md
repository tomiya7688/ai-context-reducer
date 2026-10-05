# Decide What You Need to Check First

> Japanese Source of Truth: [必要な確認を先に決める](../jp/必要な確認を先に決める.md)

Before investigating, decide which facts are essential to the decision at hand. Once you know what is needed, you can look for missing information instead of reading every document that might be related. For deciding when to stop after checking those facts, see [Decide When to Stop Exploring](exploration-control.md).

## Example: changing tax rounding on an invoice

Suppose you need to change when tax amounts on an invoice are rounded. Before starting, decide that you need to know:

- whether the specification rounds each item or the total
- where the tax calculation is implemented
- how to check a value that produces a fractional amount

Start with the specification, the calculation, and its relevant test. If they all agree on the rounding rule, you do not need to read every screen description or old discussion about invoices. If the specification and implementation conflict, or a test exposes a problem, inspect only the sources needed to resolve that discrepancy.

## Information needed now and information that can wait

The required information depends on the task. A bug in one function may require only the requirement, the target code, and its relevant test. A change to a data format may also require the readers, writers, and compatibility rules.

Once you have enough to decide, history, neighboring feature guides, and broad design documents can wait until there is a reason to read them. Before another search or read, state which question it will answer. If there is no clear answer, consider stopping before adding more material.

This is not a limit on the number of searches or words. Further investigation is necessary when a change affects a shared feature, sources disagree, a check fails, or an unknown could cause data loss or expose information. Do not mark something as verified if you could not check it; record it as unknown.

Small, obvious changes do not need a written checklist or a tracking note. Write down the required checks only when it is hard to tell how far the investigation should go.

## Example request to the AI

> Before deciding, list the questions this task must answer and the minimum evidence needed for each. Check the original sources and tests that answer them. Search further only for unresolved questions, and distinguish verified from unverified results.

## Optional tools and terminology

Use [acceptance-extractor](../../tools/common/medium/acceptance-extractor/README.md) to extract questions or completion criteria if useful. The practice of setting needed evidence in advance is called an **Evidence Budget**.
