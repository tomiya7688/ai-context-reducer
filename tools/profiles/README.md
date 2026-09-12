# Project Type Profiles

言語・規模とは別に、プロジェクトの性質から導入するツールや検証を選ぶための補助分類です。

| Type | Typical signals | Prefer |
|---|---|---|
| Game | scenes, assets, engine, gameplay | deterministic validation, visual confirmation, scene/resource map |
| GUI | views, widgets, forms, XAML | headless-first + visual confirmation |
| Compiler / Language | lexer, parser, AST, compiler | symbol/index tools, dependency graph, targeted regression |
| Data Tool | import/export, datasets, converters | dry-run, disposable workspace, generated-data validation |
| Packaged App | installer, publish, release, dist | artifact-boundary validation, artifact smoke |
| Simulation / AI | random, physics, eval, seed | deterministic seam, fixed inputs, structured observation |
| Rule-heavy | rules, protocols, specifications | Policy Routing, Responsibility Map, targeted checkers |

## Selection order

```text
repo-profile
  -> project size
project-type-profile
  -> project characteristics
language-specific tool
  -> symbols / dependencies / graph
```

複数タイプに該当してよい。たとえば Godot ゲームは `game + gui + simulation`、コンパイラ付きIDEは `compiler + gui` になり得る。

AI は検出結果を絶対視せず、README / project config / directory names と照合して必要なものだけ導入する。
