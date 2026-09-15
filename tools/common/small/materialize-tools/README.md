# materialize-tools

対象環境で利用できるportable tool implementationだけを、安全にdeployment directoryへmaterializeします。

Copier / Cookiecutter等のversioned template運用から、Context Reducerに必要な次の考え方だけを取り込みます。

- deterministic preview before apply
- source provenance
- generated/materialized file ownershipをmanifestへ残す
- existing local editsを既定で上書きしない
- update時にcreate / unchanged / conflict / overwriteを区別する

汎用template engineやproject scaffolderを再実装するものではありません。

## Implementations

共有実装にはせず、同じmaterialization contractを2実装します。

- Python: `script/materialize_tools.py`
- native Go: `acr-toolbox materialize`

Python runtimeが無い環境でも、prebuilt `acr-toolbox` 自身をbootstrap materializerとして使えます。

## Default: preview only

Python:

```sh
python script/materialize_tools.py /path/to/ai-context-reducer --out ./portable-tools
```

Native:

```sh
acr-toolbox materialize /path/to/ai-context-reducer --out ./portable-tools
```

出力は自己説明的JSONだけです。`--apply` を付けるまでfileは変更しません。

各fileは次の `planned_action` のいずれかになります。

```text
create
unchanged
conflict
overwrite
```

## Apply

Python:

```sh
python script/materialize_tools.py /path/to/ai-context-reducer \
  --out ./portable-tools \
  --apply
```

Native:

```sh
acr-toolbox materialize /path/to/ai-context-reducer \
  --out ./portable-tools \
  --apply
```

既存destinationがsourceと異なる場合は `status=conflict` として**何も上書きしません**。

上書きを明示する場合だけ `--overwrite --apply` を使います。`--overwrite` はpreview時にも利用できるため、apply前にどのfileが置換対象になるか確認できます。

## Layout

materialized layoutはwrapperが実際に参照するrepository-relative tools layoutを保ちます。

Native:

```text
portable-tools/
├─ analyze.sh or analyze.bat
└─ bin/
   └─ acr-toolbox(.exe)
```

Python fallback:

```text
portable-tools/
├─ analyze.sh or analyze.bat
└─ common/small/
   ├─ analyze-and-recommend/script/analyze_and_recommend.py
   ├─ text-search/script/text_search.py
   ├─ path-find/script/path_find.py
   ├─ tree-view/script/tree_view.py
   └─ repo-stats/script/repo_stats.py
```

以前のflat copyではwrapperの相対pathと一致せず、materialize後にwrapperが動きませんでした。現在はwrapper契約をSource of Truthとしてlayoutを維持します。

## Manifest / provenance

apply成功時に次を生成します。

```text
.acr-materialized-tools.json
```

manifest format:

```text
acr-materialized-tools-v1
```

各materialized fileについて次を残します。

```text
path
role
source_path
sha256
```

source checkoutがGit repositoryなら `source_revision` にcommit SHAを記録します。Gitが無くてもfile hashによるprovenanceは残ります。

manifestにはtimestampを入れません。同じsource revision / selected implementationなら内容が安定することを優先します。

## Replacement safety

Native版は同一directoryのtemporary fileへ書いてから置換します。既存destinationを直接truncateしません。

`os.Rename` が既存file置換を受け付けないplatformでは、既存destinationを一時backupへ退避し、新fileのinstallに失敗した場合はbackupをrestoreします。これによりWindowsでも `--overwrite` 時に古いfileを先に失う動作を避けます。

## Selection

優先順位:

```text
prebuilt native toolbox
  -> available Python runtime + selected Python fallbacks
  -> unavailable
```

runtime / package / SDKは自動installしません。

## Development routing

変更理由から読むfileを絞ります。

Python:

- environment / implementation selection / destination layout: `script/selection.py`
- preview / hash / conflict policy / apply / manifest / CLI: `script/materialize_tools.py`
- behavior validation: `tests/test_materialize_tools.py`

Native:

- CLI / apply orchestration: `tools/common/native/acr-toolbox/materialize_command.go`
- selection / hashing / preview / conflict plan / manifest model: `materialize_plan.go`
- temporary-file write / manifest write: `materialize_write.go`
- cross-platform replace / restore fallback: `safe_replace.go`
- validation: `materialize_command_test.go`

Windows replacement変更ならplannerを読む必要はなく、selection変更ならwrite pathを読む必要はありません。この分割は一般的なlayeringではなく、Context Reducer自身のTask RoutingとExploration Stopをtool開発へ適用するためです。

## Validation

Python:

```sh
python tests/test_materialize_tools.py
```

Native:

```sh
cd tools/common/native/acr-toolbox
go test ./...
```

portable native CIはLinuxとWindowsの両方で `go test ./...` を実行し、その後Windows / Linux / macOS向けbinaryをcross buildします。
