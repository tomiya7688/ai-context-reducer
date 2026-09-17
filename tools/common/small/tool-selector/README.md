# tool-selector

Context Reducer tool群の **ordered routing Source of Truth** です。

repository factsから、候補toolを単に列挙するのではなく次の順に並べます。

```text
orient -> search -> scope -> inspect -> validate -> stop
```

各tool entryは `phase / activation / availability / reason` を持ちます。別のplan配列へtool pathを重複出力しません。

Repository-level routing:

```text
python script/tool_selector.py /path/to/repo
acr-toolbox select /path/to/repo
```

Task-aware routing:

```text
python script/tool_selector.py \
  --goal "Change service behavior" \
  --task-file TASK.md \
  --changed src/service.py \
  --validation-intent targeted \
  /path/to/repo

acr-toolbox select \
  --goal "Change service behavior" \
  --task-file TASK.md \
  --changed src/service.go \
  --validation-intent targeted \
  /path/to/repo
```

`--changed` は複数回指定できます。`--validation-intent` は `unknown / targeted / full / none` です。

Task contextが1つでも与えられると、repository-level候補を全部返すのではなく、今回のtaskへ直接必要なtoolだけを `recommended_tools` に残します。各entryには `task_relevance=direct` が付きます。保留した候補を別配列へ重複出力せず、件数だけ `task_context.deferred_tool_count` に残します。

主なnarrowing:

```text
goal            -> text-search / path-find
task-file       -> acceptance-extractor / doc-index / exploration-stop-check
changed files   -> compact-diff / change-router / source-structure-index / target-slice
validation      -> validation-plan / syntax-health (利用可能な場合)
```

`availability` はexternal backendの有無も含みます。`rg` / `fd` / `scc` は未導入でもportable fallbackを使えるため正常候補です。`git-history-health` / `syntax-health` のようにexternal backendが本体となるtoolは、backendが利用可能な場合だけ通常routingへ入れます。

`exploration_stop_conditions` が満たされたら、追加のbroad explorationを続ける前に停止判断を行います。

`analyze-and-recommend` はrepository/runtime factsの収集だけを担当し、tool routingはこのtoolへhandoffします。
