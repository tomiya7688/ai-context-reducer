# 開発者・AIエージェント向け文書

このフォルダーは、このリポジトリを**変更する人とAIエージェント**（Claude、Codex、ChatGPT、Copilotなど）のための決まりを置く場所です。ai-context-reducerの手法を使いたい利用者向けの説明ではありません。利用者向けの文書は [`docs/`](../../docs/) にあり、ここには置きません。

| 文書 | 内容 |
| --- | --- |
| [workflow.md](workflow.md) | 作業の始め方から、PR・CI・自己レビュー・マージまでの手順 |
| [coding-rules.md](coding-rules.md) | コードと文書を変更するときの共通ルールと、自己レビューの観点 |
| [documentation-writing-rules.md](documentation-writing-rules.md) | 利用者向け文書を書く場合の主語・行為主体・利用者と保守者の区別 |

## 置き場所の区別

- 利用者向け: `docs/jp/`、`docs/en/`、`templates/`、`README.md`。手法の説明と導入方法だけを書き、開発手順は混ぜない。
- 開発者・AI向け: このフォルダー、ルートの `AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md`。
- 開発者向けの文書を `docs/` に置いたり、利用者向けの文書からこのフォルダーを手法として案内したりしない。
