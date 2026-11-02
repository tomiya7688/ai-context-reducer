# スキルと同梱物のライセンス一覧

ここでは、**ObaPickが作成したスキル**と、**別の公開者から取得して同梱したスキル**を区別します。GitHubで閲覧できることだけを理由に再配布してはいません。外部スキルは、公開者・実際に取得した場所・版・許可条件を調べてから取り込んでいます。

## Tomiya7688が作成したスキル

次のスキルの作成・公開者は **Tomiya7688（`tomiya7688/ai-context-reducer`）** です。ライセンスは、このリポジトリにある[MIT License](../LICENSE)です。

| スキル | 原本 |
| --- | --- |
| `obapick-find-code` | [SKILL.md](obapick-find-code/SKILL.md) |
| `obapick-small-change` | [SKILL.md](obapick-small-change/SKILL.md) |
| `obapick-review-changes` | [SKILL.md](obapick-review-changes/SKILL.md) |
| `obapick-handoff` | [SKILL.md](obapick-handoff/SKILL.md) |
| `obapick-clear-docs` | [SKILL.md](obapick-clear-docs/SKILL.md) |
| `obapick-python-check` | [SKILL.md](obapick-python-check/SKILL.md) |
| `obapick-go-check` | [SKILL.md](obapick-go-check/SKILL.md) |

## Tomiya7688以外が公開したスキル

### bug-reproduction-brief

| 項目 | 内容 |
| --- | --- |
| 同梱ファイル | [`skills/bug-reproduction-brief/SKILL.md`](bug-reproduction-brief/SKILL.md) |
| **実際の配布元・公開者** | **GitHub, Inc.** が公開するコミュニティ提供のスキル集 **[github/awesome-copilot](https://github.com/github/awesome-copilot)** |
| **実際に取得したファイル** | [github/awesome-copilot の SKILL.md（取得した版へ固定）](https://github.com/github/awesome-copilot/blob/60764df8b04cec728fd106744f98f90e18479105/skills/bug-reproduction-brief/SKILL.md) |
| **取得元のコミット** | `60764df8b04cec728fd106744f98f90e18479105` |
| 未改変の原本のGit blob SHA | `add9ca292293ef860cb4cab05063b922c49d3c1f` |
| 取得日 | 2026年11月3日 |
| **元スキルに記載された別の公開者** | **[skyestrela/ai-agent-skill-preview](https://github.com/skyestrela/ai-agent-skill-preview)**。配布元の`SKILL.md`自身がこのMITライセンスの公開スキルを出典として挙げています。元公開者の著作をGitHubだけの成果と扱いません |
| 適用ライセンス | **MIT**（配布元リポジトリと、元スキルの公開元の双方で確認） |
| 配布元の著作権・ライセンス文 | [github/awesome-copilot の MITライセンス全文](licenses/github-awesome-copilot-MIT.txt) |
| 元の公開元の著作権・ライセンス文 | [skyestrela/ai-agent-skill-preview の MITライセンス全文](licenses/skyestrela-ai-agent-skill-preview-MIT.txt) |
| 改変の有無 | **未改変**。取得した`SKILL.md`をそのまま同梱。本文の説明と出典表示も残しています |
| 自動で実行するプログラム | **なし**。スキル本文はAIに渡す作業手順で、追加の実行プログラムは同梱していません |

配布元の原本とライセンスは次の場所から確認できます。

- [GitHub側の原本](https://github.com/github/awesome-copilot/blob/60764df8b04cec728fd106744f98f90e18479105/skills/bug-reproduction-brief/SKILL.md)
- [GitHub側のライセンス](https://github.com/github/awesome-copilot/blob/60764df8b04cec728fd106744f98f90e18479105/LICENSE)
- [元公開元のリポジトリ](https://github.com/skyestrela/ai-agent-skill-preview)
- [元公開元のライセンス（取得時点のコミット）](https://github.com/skyestrela/ai-agent-skill-preview/blob/c8074b416a216ec6e47a2f34135ae3827c32b02b/LICENSE)

## ライセンスが異なる素材について

このライセンス一覧は **`skills/` の同梱物**を対象にします。ObaPickのマスコット画像は、この一覧の対象ではなく、別途[Tomiya Character Licenseの案内](../assets/README.md)に従います。

新しい外部スキルを同梱する場合は、**元の公開者と著作権者、取得した実体、固定した版、ライセンス全文、改変の有無**をここへ追加してください。再配布の許可が確認できないものはコピーせず、元の公開場所へのリンクだけにとどめます。
