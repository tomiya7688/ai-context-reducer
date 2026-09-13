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

## Architecture routing profiles

Project typeとは別に、責務境界や正式な通信経路が明確な設計では architecture routing profile を置けます。

最初の実例として `upd-commander.json` を用意しています。

このprofileは UI / Process / Data と Commander / Messenger / Processing を分類し、変更箇所から最初に読むscopeを絞るために使います。

```text
python tools/common/medium/architecture-boundary-router/script/architecture_boundary_router.py \
  --profile tools/profiles/upd-commander.json \
  src/ui/MenuCommander.cs src/process/GameMessenger.cs
```

profileは原典のarchitecture/specificationを置き換えません。あくまで最初のworking setを選ぶrouting hintです。分類できない場合やcontract変更が疑われる場合は、原典へ戻って確認します。

## Selection order

```text
repo-profile
  -> project size
project-type-profile
  -> project characteristics
architecture routing profile
  -> responsibility / boundary hints when available
language-specific tool
  -> symbols / dependencies / graph
```

複数タイプに該当してよい。たとえば Godot ゲームは `game + gui + simulation`、コンパイラ付きIDEは `compiler + gui` になり得る。

AI は検出結果を絶対視せず、README / project config / directory names と照合して必要なものだけ導入する。
