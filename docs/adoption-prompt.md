# 導入プロンプト

この文書は、Codex / Claude Code / ChatGPT などへ `ai-context-reducer` を短いコンテキストで導入させるための入口です。

導入判断の詳細は [`adoption-priority.md`](adoption-priority.md) を参照します。

## 推奨プロンプト

```text
次の ai-context-reducer 方針をこのプロジェクトへ導入してください。
https://github.com/tomiya7688/ai-context-reducer

ただし全部入りにはしないでください。
まず ai-context-reducer の README、docs/adoption-priority.md、templates/AI_CONTEXT.md だけを入口として読み、対象プロジェクトは shallow inspection から始めてください。

対象プロジェクトについて、規模・docs量・Issue量・複数AI/remote編集・GUI/interactive・非決定性・生成成果物・規約量などを短く判定し、効果が高い手法だけ選んでください。

必須コア:
- 小さいAI入口 / AI_CONTEXT
- Search first, read second
- Goal / Required / Acceptance が揃ったら探索停止
- Source of Truth
- unrelated refactor を混ぜない
- targeted validation と Unverified areas

追加手法は adoption-priority.md の条件に合う場合だけ導入してください。
リポジトリ全体、全docs、全Issuesを無条件に読まないでください。
既存の AGENTS.md / CLAUDE.md / README / docs 構造を壊さず、必要ならそれらを再利用してください。

導入後は次だけ簡潔に報告してください。
- Adopted
- Skipped
- Why
```

## AIに期待する導入手順

```text
1. ai-context-reducer の入口3ファイルだけ読む
2. 対象repoを shallow inspection
3. project signals を分類
4. A Core を導入
5. B / C は効果が高いものだけ追加
6. AI入口から source / tests / source of truth へ到達できるか確認
7. Adopted / Skipped / Why を報告
```

対象repoの初期確認は、root構成、README、既存AI指示、docs名・見出し、tests、build/package metadata 程度から始めます。

## 最小プロジェクトの場合

小規模repoでは `AI_CONTEXT.md` 相当と基本ルールだけで終了して構いません。

Task Routing、Source Structure Index、Responsibility Map、専用toolなどを「標準だから」という理由だけで追加しません。

## 大規模プロジェクトの場合

対象箇所へ到達するために毎回広い探索が必要なら、Responsibility Map、Task / Change Routing、Current State、Source Structure Index、split Context Pack などを段階的に追加します。

複数AI・複数チャット・複数開発者がremoteを更新する場合は、規模に関係なく Remote Delta First を優先します。

## やらないこと

- 導入前に対象repo全体を精読する
- ai-context-reducer 自体を全ファイル読む
- `AI_CONTEXT.md` に設計書全文をコピーする
- AI専用文書を大量に増やす
- 小規模repoへ大規模repo向け仕組みを強制する
- 既存文書構造を理由なく再編する
- 効果を説明できない自動化を追加する

## 成功条件

導入後、AIが次を短時間で判断できれば十分です。

- 今回何を達成するか
- どこを最初に読むか
- どこは通常読まないか
- source of truth はどこか
- どのsource / testsが今回のworking setか
- いつ探索を止めるか
- 何を検証すれば完了か

この状態を、対象プロジェクトに必要な最小構成で作ることが目標です。
