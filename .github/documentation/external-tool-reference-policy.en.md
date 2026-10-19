# Naming external tools in user documentation

This policy is for contributors who add named tools or links to user-facing documentation. It describes an editing rule for this repository, not a method for users, so it does not belong under `docs/`.

As a rule, a tool used as a concrete example should:

- be free to use;
- allow commercial use;
- require no credit in ordinary output or the user interface; and
- be easy to adopt, preferably as a standalone executable or through a package manager.

Do not name a tool as an example if its terms cannot be confirmed. “Requires no credit” means ordinary use does not require attribution in output, the interface, or a README. If redistribution of the tool itself requires retaining a license notice, check that separately from development-only use.

Include only examples directly relevant to the explanation. Do not add a name or link when free or commercial use is not assured, terms vary by use, explicit attribution is required, a persistent service or heavy server setup is needed despite a lightweight equivalent, or usage terms cannot be confirmed.

Prefer official sources when checking terms. Remove or replace an example if its terms change. User documentation should explain the method so it can still be used without any particular tool.
