# v1.0.0 Release Validation

v1.0.0 のユーザー配布内容に対する最終検証記録です。

## Released commit

- tag: `v1.0.0`
- commit: `751ee5e8b25a86afd4086a39cb95eba1a5bd22d1`

## Original release gate

Release作成時の `Release v1 distribution` workflow runでは、次がすべてsuccessでした。

- Source validation
- Distribution E2E / linux-x64
- Distribution E2E / linux-arm64
- Distribution E2E / windows-x64
- Distribution E2E / windows-arm64
- Distribution E2E / macos-x64
- Distribution E2E / macos-arm64
- Verify complete v1 user distribution
- Check v1 release readiness
- Promote validated v1.0.0

## Strengthened post-release gate

Release後にcompletion CIをさらに強化し、archive作成前のbundleだけでなく、archiveを再展開した実際のユーザー配布状態に対しても同じfull acceptance suiteを再実行するようにしました。

Strengthened validation commit:

- `a7ced62f0b0e5e7c625d276a013ad8824549c6fd`

Strengthened workflow result:

- Source validation: success
- Distribution E2E / linux-x64: success
- Distribution E2E / linux-arm64: success
- Distribution E2E / windows-x64: success
- Distribution E2E / windows-arm64: success
- Distribution E2E / macos-x64: success
- Distribution E2E / macos-arm64: success
- Verify complete v1 user distribution: success

## Released artifact equivalence

Released commitからstrengthened validation commitまでの差分は次だけです。

- `.github/workflows/release.yml` のarchive再展開後full E2E追加
- `release/READY_1.0.0` の削除

tool source、README、release manifest、bundle contentに変更はありません。

したがって、strengthened completion CIで検証したユーザー配布内容は公開済みv1.0.0と同一です。

## Distribution contents

Source of Truth: `release/RELEASE_MANIFEST.json`

各platform archiveには次を含みます。

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`
- `README.md`
- `TOOLS_README.md`
- `LICENSE`
- `RELEASE_MANIFEST.json`

Releaseには6platform archiveと `SHA256SUMS` を添付します。

## Policy

v1.0.0以降は、release promotion用markerをcompletion CIより先に置きません。

今後のreleaseでは、

```text
release contents fixed
  -> bug check
  -> source validation
  -> native distribution E2E on every supported platform
  -> archive
  -> re-extract archive
  -> full acceptance against extracted distribution
  -> complete release-set verification
  -> explicit promotion
```

の順序を守ります。
