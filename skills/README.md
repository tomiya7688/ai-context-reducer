# ObaPick スキルセット

[English](README.en.md)

あなたは、AIへコードの調査・修正・確認などを頼むための**短い作業手順（スキル）**を、このフォルダーから選べます。スキルは`SKILL.md`というファイルで、AIが何をすべきかと、いつ使うかを説明します。

**あなたは必要なスキルを一つ選んでコピーするだけで始められます。** ObaPickの`tools/`にあるプログラムを実行する必要も、追加のプログラムをインストールする必要もありません。スキル自体はAIへの指示であり、ファイル検索やテストは、あなたのAIが使える機能と権限の範囲で行います。

## まず一つ使う

1. [ObaPickのリポジトリ](https://github.com/tomiya7688/ai-context-reducer)をダウンロードしてください。GitHubの`Code` → `Download ZIP`から取得できます。
2. ダウンロードしたObaPickの`skills/`で、今の仕事に合う**スキルのフォルダーを一つ**選んでください。例えば`obapick-find-code/`です。
3. あなたが普段AIに作業させるプロジェクトの、下表にあるフォルダーへ、**選んだフォルダーごと**コピーしてください。`SKILL.md`だけをほかのファイルと混ぜず、同じ名前のフォルダーに置きます。
4. AIを起動し、「`obapick-find-code`を使って、設定を読み込むコードと関連テストを探してください」と依頼してください。AIのスキル一覧に現れない場合は、対応する保存場所と再読み込み方法を使っている製品の公式資料で確認してください。

| あなたが使うAI | プロジェクト内のコピー先 | 公式資料 |
| --- | --- | --- |
| **Codex** | `.agents/skills/obapick-find-code/SKILL.md` | [Codexのスキル](https://developers.openai.com/codex/skills) |
| **Claude Code** | `.claude/skills/obapick-find-code/SKILL.md` | [Claude Codeのスキル](https://code.claude.com/docs/en/skills) |
| **GitHub Copilot** | `.github/skills/obapick-find-code/SKILL.md` | [GitHub Copilotのスキル](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |
| **Gemini CLI** | `.agents/skills/obapick-find-code/SKILL.md` | [Gemini CLIのスキル](https://geminicli.com/docs/cli/skills/) |

コピー先は**あなた自身の開発プロジェクト**です。ObaPickの`skills/`は配布元であり、ここへ置いたままでは、すべてのAIが自動的に読み込むわけではありません。保存場所は製品・版で変わることがあります。

### コマンドで一つコピーする場合

次はObaPickを展開したフォルダーで実行する例です。`../my-project`を、あなたのプロジェクトの場所へ変更してください。**CodexまたはGemini CLI向け**の例なので、Claude CodeやCopilotでは上の表に従ってコピー先を変えます。

Linux・macOS：

```sh
mkdir -p ../my-project/.agents/skills
cp -R skills/obapick-find-code ../my-project/.agents/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "../my-project/.agents/skills"
Copy-Item -Recurse "skills/obapick-find-code" "../my-project/.agents/skills/"
```

すでに同名のスキルがある場合は、内容を確認してから置き換えてください。他のAI向けの指示書を消す必要はありません。

## どのスキルを選ぶか

| こんなとき | スキル |
| --- | --- |
| 修正前に、関係するコードやテストを探したい | [obapick-find-code](obapick-find-code/SKILL.md) |
| 変更対象が分かっていて、小さく修正したい | [obapick-small-change](obapick-small-change/SKILL.md) |
| 変更差分やテスト結果をレビューしたい | [obapick-review-changes](obapick-review-changes/SKILL.md) |
| 作業を途中で止め、次のAIへ引き継ぎたい | [obapick-handoff](obapick-handoff/SKILL.md) |
| READMEや説明文の主語・操作を明確にしたい | [obapick-clear-docs](obapick-clear-docs/SKILL.md) |
| Pythonの変更に合う検査を行いたい | [obapick-python-check](obapick-python-check/SKILL.md) |
| Goの変更に合う検査を行いたい | [obapick-go-check](obapick-go-check/SKILL.md) |
| 不具合の再現手順を、修正前に確認したい | [bug-reproduction-brief](bug-reproduction-brief/SKILL.md) **（外部OSS・英語原文）** |

最初から全スキルを導入する必要はありません。例えばPythonの不具合なら、まず再現に必要な`bug-reproduction-brief`、修正時に`obapick-python-check`というように、**作業に必要なものだけ**使えます。

## スキルができること・できないこと

スキルは「必要なときにAIが読む作業手順」です。スキルを置いただけでAIにファイルの閲覧・編集・コマンド実行の権限が追加されるわけではありません。対応する機能がないAIを使っている場合は、あなたが必要なファイルや検査結果を渡してください。

スキルは、プロジェクト固有の規則や安全上の確認を置き換えません。AIが作業を終えたら、**あなたは実際の変更差分と検査結果を確認してください**。結果の省略や未検証の成功宣言を許さないでください。

使うスキルが増えると、各スキルの名前と説明を読む量も増える場合があります。使わないスキルはコピーしない方が、ObaPickの目的にも合います。

## 作者とライセンス

ObaPickが作成したスキルは、リポジトリの[MIT License](../LICENSE)に従います。他の公開者が作ったスキルは、**公開者・元の配布場所・取得した版・著作権表示・ライセンス**を[ライセンス一覧](LICENSES.md)に記録しています。

外部スキルの内容は、**同梱前にあなた自身でも確認できます**。ライセンスを確認できないものは同梱していません。外部の作者による成果を、ObaPickが独自に作成したものとは表示しません。
