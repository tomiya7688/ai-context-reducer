# Releasing v1.x

v1.0.0は最初のユーザー配布版です。v1.0.xのパッチ版は、公開CLI / JSON contract / bundle contentsを維持した保守変更として同じcompletion gateで検証します。

## Release gate

Release作成前に `.github/workflows/release.yml` の全jobがgreenであることを必須とします。

完了用CIは次を検証します。

1. repository consistency / `git diff --check`
2. 全Python toolのcompile + test
3. 全Go moduleのtest
4. Windows x64 / arm64、Linux x64 / arm64、macOS x64 / arm64でnative build
5. 各platformの配布binaryを使ったE2E
6. Small / Medium language fallback
7. policy success / violation exit code
8. template generate / check / drift detection
9. scoped guide resolution
10. search / find / routing / context / Git系の主要command
11. standalone Go toolsの実動作
12. archive化後の再展開と必須ファイル確認
13. 6archiveの存在確認
14. `SHA256SUMS` 生成

ひとつでも失敗した場合、Release jobは実行されません。

## User distribution

`release/RELEASE_MANIFEST.json` を現在のv1.0.x配布内容のSource of Truthとします。

必須内容:

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`
- `README.md`
- `TOOLS_README.md`
- `LICENSE`
- `RELEASE_MANIFEST.json`

Windows executableには `.exe` suffixを付けます。

## Platforms

```text
ai-context-reducer-v<version>-windows-x64.zip
ai-context-reducer-v<version>-windows-arm64.zip
ai-context-reducer-v<version>-linux-x64.tar.gz
ai-context-reducer-v<version>-linux-arm64.tar.gz
ai-context-reducer-v<version>-macos-x64.tar.gz
ai-context-reducer-v<version>-macos-arm64.tar.gz
SHA256SUMS
```

現在のcandidate versionは `release/RELEASE_MANIFEST.json` の `release_version` と一致させます。

## Candidate validation

mainへのrelease関連変更でも同じcompletion workflowを実行します。この場合はReleaseを公開せず、`v1-release-candidate` artifactだけを生成します。

main上のcandidate CIがgreenでも、tagやGitHub Releaseを自動作成しません。

## Publishing

公開は必ず明示操作を起点にします。

```text
main candidate CI green
  -> 配布内容とbug checkを最終確認
  -> 人がrelease tagを作成してpush
  -> tag commit上でcompletion workflowを再実行
  -> 全job success
  -> GitHub Releaseを作成
```

`v1.0.0` 以降、main pushやREADY markerからtag/Releaseを自動promotionする経路は持ちません。

workflow_dispatchからpublishする場合も、matching tagがrepositoryに存在することを必須とします。

## Post-release

v1.0.0後の新言語対応、外部backend追加、heuristic改善は新しいIssueとして管理します。patch releaseの完了条件へ新機能を後付けしません。


## v1.0.0 validation record

公開済みv1.0.0の最終検証記録は [`release/validation/v1.0.0.md`](../release/validation/v1.0.0.md) を参照してください。
