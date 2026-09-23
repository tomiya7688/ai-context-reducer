# Full Bundle 配布設計

この文書は v1.1.0 で追加する Full Bundle の配布契約を定義します。

Full Bundle は通常版を置き換えるものではありません。通常版は軽量なCLI配布として維持し、Full Bundle はその内容をそのまま含んだ上で、GUI Hub、Python fallback、言語固有tool、setup script、profiles、templates、利用者向けdocsを追加する上位集合とします。

配布内容の機械可読な Source of Truth は release/FULL_BUNDLE_MANIFEST.json です。

## 1. 通常版との関係

通常版の配布契約は引き続き release/RELEASE_MANIFEST.json が Source of Truth です。

Full Bundle のrootには、通常版と同じ次のfileを同じ名前で置きます。

~~~text
acr-toolbox(.exe)
go-symbols(.exe)
go-import-map(.exe)
go-package-graph(.exe)
affected-tests(.exe)
README.md
TOOLS_README.md
LICENSE
RELEASE_MANIFEST.json
~~~

そのため、通常版で使えていたCLI commandをFull Bundleでも同じように実行できます。Windowsでは実行fileに .exe suffixを付けます。

Full Bundleだけに必要な情報は FULL_BUNDLE_MANIFEST.json へ分離し、通常版manifestへGUIやfallbackの一覧を混ぜません。

## 2. directory layout

最終的なv1.1.0 Full Bundleは次のlayoutを標準とします。

~~~text
ai-context-reducer-full-v1.1.0-<platform>/
├─ acr-toolbox(.exe)
├─ go-symbols(.exe)
├─ go-import-map(.exe)
├─ go-package-graph(.exe)
├─ affected-tests(.exe)
├─ README.md
├─ TOOLS_README.md
├─ LICENSE
├─ RELEASE_MANIFEST.json
├─ FULL_BUNDLE_MANIFEST.json
├─ setup.sh
├─ setup.bat
├─ analyze.sh
├─ analyze.bat
├─ gui/
│  └─ acr-hub(.exe)
├─ fallback/
│  └─ python/
│     ├─ common/
│     └─ languages/
│        ├─ python/
│        ├─ c/
│        ├─ cpp/
│        ├─ csharp/
│        └─ gdscript/
├─ profiles/
├─ templates/
└─ docs/
   ├─ jp/
   └─ en/
~~~

GUI実装内部のasset配置は #25 / #26 で決めて構いません。ただし利用者が起動するplatform固有entrypointは gui/acr-hub(.exe) とし、追加runtimeを利用者へ要求しない配布物にします。

## 3. Go製tool

Full Bundleに含めるGo製toolは、各platformでbuild済みbinaryだけです。

- acr-toolbox
- go-symbols
- go-import-map
- go-package-graph
- affected-tests

Full Bundleへ *.go / go.mod / go.sum / build script / Go unit test source / Go build cache は含めません。利用者へ go build を要求しません。

Go toolchainが無い環境でも、対応platformのFull Bundleに含まれるCLIとGUIを利用できることをrelease conditionとします。

## 4. Python fallback

Python実装はfallback / 参照実装として同梱します。

~~~text
tools/common/...   -> fallback/python/common/...
tools/python/...   -> fallback/python/languages/python/...
tools/c/...        -> fallback/python/languages/c/...
tools/cpp/...      -> fallback/python/languages/cpp/...
tools/csharp/...   -> fallback/python/languages/csharp/...
tools/gdscript/... -> fallback/python/languages/gdscript/...
~~~

runtimeに必要な script/*.py と互換entrypoint / 必要なconfigだけを含めます。tests、cache、開発用build fileは配布しません。

Pythonが無いことはFull Bundleの通常利用を妨げません。GUIとnative CLIはPythonなしで動作させます。Python fallbackを明示利用する場合だけ、対象環境に既に存在するPythonを利用し、Full Bundle自身がPythonやpackageをinstallしません。

## 5. setup / analyze entrypoint

Full Bundle rootに setup.sh / setup.bat / analyze.sh / analyze.bat を置きます。これらはFull Bundle内のprebuilt acr-toolboxを第一候補にします。

wrapperはbundle内native binaryの解決、引数透過、nativeが本当に利用不能な場合のoptional Python fallbackだけを担当し、分析ロジックを重複実装しません。

## 6. GUI Hub

GUI Hubは既存CLIのfrontendです。

~~~text
GUI action
  -> existing CLI
  -> existing JSON contract
  -> GUI presentation
~~~

GUI専用の分析ロジックをFull Bundle contractには追加しません。CLI単体利用、stdout / stderr / exit code、既存JSON contractを維持します。

Large / heavy解析やSDK / runtime / external toolのinstallはGUIからも自動実行しません。GUI実装の詳細は #25-#27 で行います。

## 7. profiles / templates

profiles/ はproject typeやarchitecture routing用の補助入力を置く場所です。profileは必須にしません。templates/ はAI入口やContext Pack等のcanonical templateを配布します。

repository側に新しい配布対象profile / templateを追加する場合は、Full Bundle manifestを同じchange setで更新します。

## 8. docs

Full Bundleの利用者向けdocsは最終的に docs/jp/ と docs/en/ へ配置します。docs/jp/ を日本語Source of Truth、docs/en/ を翻訳として扱う方針は #28-#31 で具体化します。

repository内部のrelease validation記録やtest fixtureまで無条件に同梱しません。

## 9. 外部runtime / SDK / tool

Full Bundleは全部入りですが、すべての外部dependencyを同梱する意味ではありません。

Go toolchain、Python runtime、dotnet SDK、C/C++ compiler、Godot、SCIP indexer、Universal Ctags、ast-grep、rg / fd / scc等を勝手にinstallしません。

既に利用可能なら高精度backendとして使い、存在しない場合はportable native pathまたは利用可能なfallbackへ戻ります。

## 10. 自動実行境界

Full Bundleに含まれていることと、自動実行してよいことは別です。自動実行してよいのはcheap / shallowな既存経路だけです。

~~~text
project facts
  -> recommendation
  -> user selects Run
~~~

Medium / Large / heavy解析、外部compiler / SDKを使う処理、書込みを伴う処理は既存の安全境界を維持します。GUIのAnalyzeも全tool一括実行にはしません。

## 11. manifestの役割

release/FULL_BUNDLE_MANIFEST.json は supported platform、通常版との互換関係、build済みnative binary、GUI entrypoint、setup wrapper、Python fallbackのsource -> bundle path、profiles / templates、docs tree、禁止配布内容、runtime / auto-install / heavy execution policyを定義します。

tree inclusion ruleはbuild時に展開し、release CIでは最終archiveの実file一覧と照合します。この照合自体は #32-#34 で実装します。

## 12. compatibility rule

Full Bundleの追加で既存CLIを壊しません。

- rootの5 binary名を維持する
- subcommand / argument / exit codeを維持する
- machine outputは tools/JSON_CONTRACT.md を維持する
- Full Bundle専用GUIをCLIのSource of Truthにしない
- 通常版を継続して別archiveとして配布できる
- Full Bundleにしかない補助fileを通常版へ必須化しない

v1.1.0でCLI contract変更が必要になった場合は、Full Bundle追加の副作用として行わず別の明示Issueで扱います。
