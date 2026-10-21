# architecture-boundary-router

プロジェクトに既にある機能分担やデータの流れを読み、変更したファイルに関係する機能と最初に読むファイルの候補を表示します。特定の設計への適合性は判定しません。使い方は[機能ごとのコードの分け方から読む場所を決める](../../../../docs/jp/手法/機能ごとのコードの分け方から読む場所を決める.md)を参照してください。

## 変更時に読む場所

- CLI / output変更: `script/architecture_boundary_router.py`
- profile読込・外部I/O変更: `script/messenger.py`
- path分類・hint意味論変更: `script/processing.py`
- profile→routesのflow変更: `script/commander.py`

この分け方により、変更した機能の担当箇所から読み始め、関係が見つかった範囲へ調査を広げられます。
