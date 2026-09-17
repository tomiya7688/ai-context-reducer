# analyze-and-recommend

Repository / runtime factsを安価に集めるfirst-pass analyzerです。

このtoolはtool routingのSource of Truthではありません。出力の `routing_handoff` から `tool-selector` / `acr-toolbox select` へ進みます。

```text
python script/analyze_and_recommend.py /path/to/repo
acr-toolbox analyze /path/to/repo
```

主な出力:

- repository size class / file counts
- language mix
- docs / tests / large-file counts
- project-type signals
- Git availability / dirty state
- available external tools
- runtime implementation plan
- routing handoff

tool recommendationや実行順をここへ重複保持しません。ordered routingは `tool-selector` が担当します。
