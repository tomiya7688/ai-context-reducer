# tool-selector

Context Reducer tool群の **ordered routing Source of Truth** です。

repository factsから、候補toolを単に列挙するのではなく次の順に並べます。

```text
orient -> search -> scope -> inspect -> validate -> stop
```

各tool entryは `phase / activation / availability / reason` を持ちます。別のplan配列へtool pathを重複出力しません。

```text
python script/tool_selector.py /path/to/repo
acr-toolbox select /path/to/repo
```

`availability` はexternal backendの有無も含みます。`rg` / `fd` / `scc` は未導入でもportable fallbackを使えるため正常候補です。`git-history-health` / `syntax-health` のようにexternal backendが本体となるtoolは、backendが利用可能な場合だけ通常routingへ入れます。

`exploration_stop_conditions` が満たされたら、追加のbroad explorationを続ける前に停止判断を行います。

`analyze-and-recommend` はrepository/runtime factsの収集だけを担当し、tool routingはこのtoolへhandoffします。
