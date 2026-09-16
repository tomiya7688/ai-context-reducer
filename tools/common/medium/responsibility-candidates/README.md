# responsibility-candidates

Repository内のcode fileから、Responsibility Mapを作り始めるためのMarkdown tableを生成します。

このtoolは責務そのものを推測しません。file path / sizeだけを並べ、`Responsibility` は人間またはagentがSource of Truthを確認して埋めるためのTODOにします。

## Usage

```text
python script/responsibility_candidates.py . --max 120
```

出力そのものがMarkdown artifactなのでJSON化しません。

## Context Reducer behavior

- internal code-file scanは既定でunlimited
- `--max` はagent-visible table rowsだけをboundedにする
- `--max-scan-files` は明示的なperformance/safety capで、既定0=unlimited
- 実際に追加code fileが存在する場合だけscan truncationを明示する
- stat/walk failureをsize=0や正常scanとして隠さない
- missing/non-directory rootはstderr + non-zero exit

`--max-scan-files` を小さくしてrouting候補を落とすより、通常はfull internal scanしてMarkdown出力だけを絞ります。

## Development routing

Python版は小さな単一責務toolなので形式的に分割しません。

```text
scan / ranking / Markdown CLI -> script/responsibility_candidates.py
contract validation           -> tests/test_responsibility_candidates.py
```
