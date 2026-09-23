# Remote Context / Remote Delta First

複数の AI、チャット、開発者が同じリポジトリを更新する場合、作業開始時のローカル状態が最新とは限りません。

このため、実装前にリポジトリ全体を再読込するのではなく、まず remote との差分を小さな要約として取得する方式を推奨します。

## 基本フロー

```text
local HEAD
   +
remote HEAD
   +
merge base
   ↓
remote commits
changed files
diff stat
bounded diff excerpt
   ↓
現在タスクに関係する変更だけ読む
```

重要なのは、最初から full diff や変更ファイル全文を読むことではありません。

まず次のような compact remote context を確認します。

- local / remote の識別子
- ahead / behind 状態
- remote commit subjects
- changed file names / status
- diff stat
- 上限付きの diff excerpt

これで不足する場合のみ full diff や対象ファイルへ広げます。

## Bounded diff

差分抜粋には上限を設けます。

目的は完全なレビューではなく、「どこが変わったか」「現在タスクに影響するか」を低コストで把握することです。

上限を超えた部分は省略したことが明確に分かる形にし、必要なら原典へ戻れるようにします。

## Safe update

remote をローカルへ反映する自動化を行う場合は、破壊的な自動解決を避けます。

推奨ルール:

- dirty worktree では自動更新しない
- local に remote 未反映の commit がある場合は自動更新しない
- fast-forward のみ許可する
- conflict / divergence は人間または明示的な判断へ戻す

コンテキスト削減のために状態を勝手に変更してはいけません。

## Read changed files selectively

remote context を確認した後も、変更された全ファイルを読む必要はありません。

現在タスクと関係する changed files を優先し、必要な直接依存だけ追加します。

```text
remote delta
  -> relevant changed files
  -> direct dependencies
  -> full diff / additional docs only when needed
```

## 標準化レベル

### 標準推奨

- 作業開始時に remote 差分の存在を確認できるようにする
- full diff より compact remote summary を先に使う
- diff excerpt は bounded にする
- 自動更新は fast-forward のみに限定する
- dirty / diverged 状態では停止する

### 任意実装

- `git fetch` を行う補助ツール
- remote commit / changed files / stat / excerpt の自動表示
- safe fast-forward オプション
- remote context の Context Pack への自動挿入

Git、GitHub、特定OS、特定AIへの依存は標準必須にはしません。
