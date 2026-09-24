# Syntax Health Validation

> Japanese Source of Truth: [構文チェックを軽い検証に使う](../jp/構文チェックを軽い検証に使う.md)

This method uses syntax / parser health as low-cost validation evidence so that obvious failures can be found without loading parse trees or large lists of healthy files.

Syntax Health is part of [Validation Routing](validation-routing.md).

> **A successful syntax check does not prove semantic correctness, type correctness, runtime behavior, or task Acceptance.**

Use it as cheap validation, then route to the targeted tests / compiler / runtime / artifact validation required by the change.

## 1. Purpose

After editing source, checking that the source is syntactically valid can often be much cheaper than broader validation.

~~~text
changed source
  -> cheap syntax / parser health
  -> syntax issue?
       yes -> fix / inspect failing files
       no  -> proceed to required semantic validation
~~~

If parser results are reduced to only the files with problems, there is no need to pass the full parse tree or a list of every healthy file to the AI.

The purpose is not to shrink validation down to syntax checks. It is to **catch cheap failures early, then run the required higher-cost validation in the right scope**.

## 2. When it is useful

Syntax Health is useful when:

- a parser / compiler frontend for the target language is already available
- changed source can be checked syntactically
- syntax failures can be reported in a targeted way
- it is cheaper than a full build / full test and can run first
- a health summary is sufficient for the initial decision instead of the full parse tree

Examples:

- cheap gate immediately after editing several source files
- checking whether generated source parses
- syntax regression check after a merge / mechanical edit
- eliminating obvious parse errors before a full test run

## 3. What syntax success does not prove

Do not infer from syntax health success that:

- type checking passes
- import / dependency resolution is correct
- referenced symbols exist
- API contracts are compatible
- business logic is correct
- tests pass
- the program starts at runtime
- performance requirements are satisfied
- packaging / distribution is correct
- UI / visual behavior is correct

~~~text
syntax valid
  != semantic correct
  != behavior correct
  != task complete
~~~

Never use syntax checks alone as completion evidence.

## 4. Position inside Validation Routing

Validation Routing selects required evidence from the change type.

Syntax Health is one form of cheap static evidence.

~~~text
change type
  -> syntax health when useful and available
  -> targeted semantic validation
  -> broader validation only when required
  -> completion evidence
~~~

### Pure logic change

~~~text
syntax health
  -> targeted unit / regression tests
~~~

### Typed / compiled language change

~~~text
syntax / parser health
  -> compiler / type checker
  -> targeted tests
~~~

A parser alone does not prove type / symbol resolution.

### Runtime behavior change

~~~text
syntax health
  -> targeted tests
  -> bounded runtime / smoke
~~~

When Acceptance includes runtime behavior, execution evidence is required.

### Package / distribution change

~~~text
syntax health if source changed
  -> source tests / build
  -> artifact generation
  -> artifact smoke
~~~

Syntax success is not a replacement for artifact validation.

## 5. When no parser is available

Do not auto-install a parser / grammar / SDK just for Syntax Health.

~~~text
parser already available
  -> use cheap syntax health

parser unavailable
  -> report unavailable
  -> use existing compiler / tests / other validation path
~~~

If adding the parser is itself a Required part of the project's standard environment, handle that explicitly as a separate task.

Context Reducer tools do not install missing dependencies automatically.

## 6. Verify parser coverage

The existence of a parser executable does not prove that it correctly supports the target language / grammar / version.

Do not confuse any of the following with success:

- grammar unavailable
- parser execution failure
- unsupported syntax / language version
- malformed saved summary
- target file was not actually inspected
- 0 files observed when files should have been checked

Backend unavailable / failed / input failure is different from "0 syntax issues."

## 7. Move on to targeted validation

After syntax success, proceed to the smallest semantic evidence required for the task.

Examples:

- logic change -> matching unit / regression test
- public function / type change -> compiler + direct consumers / tests
- config / schema change -> parser/schema validation + producer / consumer tests
- dependency change -> build / dependency resolution
- runtime change -> smoke / deterministic runtime
- UI change -> automated checks + visual confirmation when Acceptance requires it
- generated artifact change -> artifact-boundary validation

Validation Routing and Acceptance decide how far to go, not Syntax Health.

## 8. When to escalate to broader / Large validation

Escalate when cheap validation cannot sufficiently cover the impact.

Examples:

- shared / core code changed
- public API / schema / protocol changed
- dependency / build / package metadata changed
- the parser / grammar / compiler itself changed
- dependencies of the changed area are unknown
- confidence in targeted-test selection is low
- syntax passes but compiler / tests fail
- cross-module / cross-package impact appears
- runtime / artifact / visual Acceptance exists
- security / compatibility unknowns remain
- the user or project completion gate requires broader validation

~~~text
cheap evidence insufficient
  -> targeted compiler / tests
  -> subsystem validation
  -> full / artifact / runtime validation only when required
~~~

Do not always start with Large validation. Escalate when the task creates a reason.

## 9. Failure context

Even when syntax issues are found, there is normally no need to output the full parse tree or all source.

Usually the following is sufficient:

- failing file
- issue count
- bounded parser diagnostic
- backend status

From there, inspect only the target file / line / surrounding source.

Do not keep long lists of healthy files in the Context Pack.

## 10. Reuse saved parser results

When CI or another stage has already produced a parser summary, reuse it.

~~~text
existing parser / CI result
  -> compact syntax health normalization
  -> agent-visible failures only
~~~

Do not reparse the same source with another tool if existing evidence is still valid.

A stale summary is not evidence for the current change.

## 11. Small repositories

If a small project's standard compiler / tests are already cheap and directly inspect the same scope, a dedicated Syntax Health step may be unnecessary.

~~~text
cheap standard validation already sufficient
  -> use it directly
~~~

Avoid increasing maintenance cost just by adding another validation stage.

## 12. Optional implementation

This repository includes `tools/common/small/syntax-health`.

It is an optional helper that reuses an already-available Tree-sitter parser / grammar or a saved summary and returns only files with syntax issues as bounded JSON.

- it does not auto-install Tree-sitter or grammars
- it does not treat backend unavailable as success
- it does not treat parser failure as zero syntax issues
- it does not return full parse trees to the agent
- it does not interpret syntax success as semantic correctness
- tool success alone is not a completion gate

If the project's compiler, IDE parser, language server, or linter provides equivalent cheap evidence, use that instead.

## 13. Standard recommendations

- use syntax / parser health as cheap validation
- prefer reuse only when a parser is already available
- do not auto-install a parser / grammar
- distinguish backend unavailable / failed from zero issues
- do not interpret syntax success as semantic / type / runtime correctness
- do not decide task completion from syntax checks alone
- proceed to targeted tests / compiler / runtime / artifact validation based on the task
- escalate for shared / public / unknown-impact changes
- return only failing files in bounded form instead of healthy parse trees
- skip a dedicated step in small repositories when standard compiler/tests are already cheap
- do not make the `syntax-health` tool the method itself
