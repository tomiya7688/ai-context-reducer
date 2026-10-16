# ObaPick 名称・見せ方の検討案

この文書は [Issue #227](https://github.com/tomiya7688/ai-context-reducer/issues/227) に基づく**公開前のレビュー案**です。現行のGitHubリポジトリ名 `ai-context-reducer` と配布物名・CLI名はそのままです。

## 何を伝える名前か

- **ObaPick（オバピック）**: 印象に残る短い名前と「必要な情報を選ぶ（pick）」を組み合わせた呼称。
- 日本語の一文: **AIに渡す情報を、必要な分だけ。**
- 英語の一文: **Give AI only the context it needs.**
- 対象読者: AIにコード・仕様・テストの調査や修正を頼む人。
- 中身: LLMの基本、作業に必要な根拠を選ぶ手法、導入用のひな型、任意の補助ツール。
- 重視すること: **必要な根拠と確認手順を残す。** 情報を闇雲に短くしたり、どんな作業でも正確さが保証されると宣伝しない。

## 見せ方

- README冒頭でマスコット、名称、一文、具体的な困りごとへの説明の順に示す。
- 画像は[提供されたマスコット素材](../assets/obapick-mascot.png)を使用し、[別ライセンス](../assets/README.md)を明記する。
- READMEの日本語版・英語版で同じ訴求を保ち、既存の検証結果・導線・手法文書は変更しない。
- 実測ベンチマークの**75.5%** は固定した合成fixtureでのAIへ渡す文字数の削減率であって、一般的なトークン消費や費用の削減率ではない。

## GitHub About に記入する案（正式採用後）

Description:

> ObaPick helps AI coding agents focus on the code, tests, docs, and evidence a task needs. Methods, templates, and optional tools.

Topics候補: `context-engineering`, `llm`, `ai-coding`, `coding-agent`, `developer-tools`, `code-search`, `context-management`。

このPRではAbout欄を変更しない。既存の [Issue #211](https://github.com/tomiya7688/ai-context-reducer/issues/211) で設定・確認する。

## 名前を確定する前の確認事項

- [ ] ユーザーが **ObaPickを正式名称として採用する** と明示する。
- [ ] 商標、一般Web検索、会社・製品の名称、ドメイン、主要SNSの同名/類似名を確認する。GitHubで完全一致が見つからないだけでは採用判断に十分でない。
- [ ] マスコット素材の正式な画像名・原作者の表記とTomiya Character License適用範囲を最終確認する。
- [ ] 初見の人が「専用ツールに入れ替える必要はなく、手法の説明を読んで試せる」と理解できるか確認する。

## 改名実施時の移行項目

正式承認後、**別Issue・別PR**として扱う。

1. GitHubのリポジトリ名変更と新旧URLの導線。
2. READMEのリンク、日本語・英語文書、関連リポジトリからの参照。
3. Releases、READMEにあるダウンロードリンク、配布物、CLIコマンド、バイナリの名称。新名称へ無条件に改名しない。既存名で動作するものは互換性を残す。
4. ベンチマークの再現コマンド、CI、補助ツールが埋め込むリポジトリパス。
5. 外部記事、既存Issue/PR、GitHub Actions、サブモジュールや利用者の固定URL。
6. GitHub Description・Topics・ソーシャルカード、画像ライセンスの分離、公開後のTraffic計測。

**未実施:** GitHubリポジトリ名の変更、既存の利用者向けコマンドの変更、リリースタグ変更、外部サイトへの告知。
