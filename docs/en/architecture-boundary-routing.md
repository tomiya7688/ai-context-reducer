# Choose What to Read from Existing Responsibilities

> Japanese Source of Truth: [既存の担当分けから読む場所を決める](../jp/既存の担当分けから読む場所を決める.md)

Large software projects often divide work among areas such as the user interface, data import, and storage. Use an existing description of those responsibilities to choose where to begin investigating. This helps you reach relevant information without rereading the structure of the entire project each time.

## Example: Fixing dates in CSV import

Suppose a CSV import shifts dates. If the project guide says that the import component handles reading and converting CSV data, start with that component and its tests. Read the screen or storage code only if you find that its connection to the importer could affect the change.

This order avoids reading descriptions of every feature, such as screens, storage, and reports, at the start. The responsibility guide is a pointer to where to begin, not proof of how the software behaves. If the implementation or tests disagree with the guide, check the actual code and tests.

## Use responsibility boundaries as a reading guide

Find the existing design or developer guide for the area related to the requested change, then start with that area's implementation and verification. If the change stays within that area, there is no need to read unrelated areas.

If the change alters an agreement between areas, such as the interface between the screen and importer or the format used for storage, one side is not enough. Check the agreement itself, both implementations, and their tests.

## When the guide is missing or does not fit

If the project has no description of its responsibilities, do not invent a structure. Find the target with ordinary search or an existing code index. Do the same when the guide is stale, the change does not fit its categories, or it fails to narrow the search.

Do not exclude a potentially affected area just to keep the reading scope small. If you discover a dependency or impact, read what is needed to check that connection. In a small project where the target and its tests are obvious, there is no need to create a separate responsibility guide.

## Example request to the AI

> Use existing component responsibilities to select the owner of this change and its direct tests. If the change crosses a boundary, identify the contract and implementation on both sides. Do not invent a new component split without evidence.

## Optional tools and terminology

Optional [architecture-boundary-router](../../tools/common/medium/architecture-boundary-router/README.md) suggests boundary candidates. This method is called **Architecture Boundary Routing**.
